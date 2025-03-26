#! /usr/bin/env python3

""" MkPyCapi のクラス定義ファイル

:file: mk_py_capi.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from .codeblock import CodeBlock, IfBlock, ElseBlock, ElseIfBlock, ForBlock
from .codeblock import FuncBlock, ArrayBlock, StructBlock, TryBlock, CatchBlock
import re
import os
import datetime
import sys
from collections import namedtuple


# 関数定義を表す型
FuncDef = namedtuple('FuncDef',
                     ['name',
                      'func',
                      'arg_list'])

FuncDef.__new__.__defaults__ = (None, None, [])

# sequence 構造体を表す型
Sequence = namedtuple('Sequence',
                      ['length',
                       'concat',
                       'repeat',
                       'item',
                       'ass_item',
                       'contains',
                       'inplace_concat',
                       'inplace_repeat'])

# メソッドを表す型
Method = namedtuple('Method',
                    ['name',
                     'func_def',
                     'is_static',
                     'has_args',
                     'has_keywords',
                     'doc_str'])

# getter/setterを表す型
GetSet = namedtuple('GetSet',
                    ['func_def',
                     'has_closure'])

# 属性を表す型
Attr = namedtuple('Attr',
                  ['name',
                   'getter_name',
                   'setter_name',
                   'closure',
                   'doc_str'])


def analyze_args(arg_list):
    """引数のリストから特徴を解析する．

    has_args, has_keywords のタプルを返す．
    """
    has_args = False
    has_keywords = False
    if len(arg_list) > 0:
        has_args = True
        for arg in arg_list:
            if arg.name is not None:
                has_keywords = True
    return has_args, has_keywords


class MkPyCapi:
    """Python 拡張用のヘッダ/ソースファイルを生成するためのクラス
    """

    def __init__(self, *,
                 classname,
                 pyclassname,
                 namespace,
                 pyname,
                 header_include_files=[],
                 source_include_files=[]):
        self.classname = classname
        self.pyclassname = pyclassname
        self.namespace = namespace
        self.typename = f'{classname}_Type'
        self.objectname = f'{classname}_Object'
        self.pyname = pyname
        self.header_include_files = header_include_files
        self.source_include_files = source_include_files

        self.__fout = None

        self.__name_dict = set()

        self.__preamble_gen = None
        self.__dealloc = None
        self.__repr = None

        self.__number_name = None
        self.number_gen = None

        self.__sequence_name = None
        self.__sequence_tbl = None
        
        self.__mapping_name = None
        self.mapping_gen = None

        self.__hash = None
        self.__call = None
        self.__str = None
        self.__richcompare = None
        self.__init = None
        self.__new = None
        self.__new = None

        self.__ex_init_gen = None
        self.__conv_gen = None
        self.__deconv_gen = None
        self.doc_str = f'{self.classname} object'

        self.__method_name = None
        self.__method_list = []

        self.__getset_name = None
        self.__attr_list = []
        self.__getter_list = []
        self.__setter_list = []

        self.__indent = 0
        self.__conv_def_pat = re.compile('^(\s*)%%CONV_DEF%%$')
        self.__deconv_def_pat = re.compile('^(\s*)%%DECONV_DEF%%$')
        self.__to_def_pat = re.compile('^(\s*)%%TOPYOBJECT%%$')
        self.__from_def_pat = re.compile('^(\s*)%%FROMPYOBJECT%%$')
        self.__tp_init_pat = re.compile('^(\s*)%%TP_INIT_CODE%%$')
        self.__ex_init_pat = re.compile('^(\s*)%%EX_INIT_CODE%%$')

    def add_preamble(self, gen_body):
        self.__preamble_gen = gen_body
        
    def add_dealloc(self, *,
                    func_name=None,
                    gen_body=None):
        """dealloc 関数定義を追加する．
        """
        if func_name is None:
            func_name = 'dealloc_func'
        self.__dealloc_name = self.__check_name(func_name)
        if gen_body is None:
            # デフォルト実装
            def dealloc_gen(gen):
                gen._write_line(f'obj->mVal.~{gen.classname}()')
            gen_body = dealloc_gen
        self.__dealloc = FuncDef(func_name, gen_body, [])

    def add_repr(self, *,
                 func_name=None,
                 repr_func):
        """repr 関数定義を追加する．
        """
        if func_name is None:
            func_name = 'repr_func'
        self.__repr = FuncDef(func_name, repr_func, [])

    def add_sequence(self, *,
                     name=None,
                     length=None,
                     concat=None,
                     repeat=None,
                     item=None,
                     ass_item=None,
                     contains=None,
                     inplace_concat=None,
                     inplace_repeat=None):
        if name is None:
            name = 'sequence'
        self.__sequence_name = name
        length = self.__complete(length, 'sq_length')
        concat = self.__complete(concat, 'sq_concat')
        repeat = self.__complete(repeat, 'sq_repeat')
        item = self.__complete(item, 'sq_item')
        ass_item = self.__complete(ass_item, 'sq_ass_item')
        contains = self.__complete(contains, 'sq_contains')
        inplace_concat = self.__complete(inplace_concat, 'sq_inplace_concat')
        inplace_repeat = self.__complete(inplace_repeat, 'sq_inplace_repeat')
        self.__sequence_tbl = Sequence(length, concat, repeat, item, ass_item,
                                       contains, inplace_concat, inplace_repeat)
        
    def add_new(self, *,
                func_name=None,
                arg_list=[],
                gen_body):
        """new 関数定義を追加する．
        """
        if func_name is None:
            func_name = 'new_func'
        self.__new = FuncDef(func_name, gen_body, arg_list)
        
    def add_method(self, name, *,
                   func_name=None,
                   arg_list=[],
                   is_static=False,
                   gen_body,
                   doc_str=''):
        """メソッド定義を追加する．
        """
        if func_name is None:
            func_name = name
        self.__check_name(func_name)
        has_args, has_keywords = analyze_args(arg_list)
        func_def = FuncDef(func_name, gen_body, arg_list)
        method = Method(name, func_def,
                        is_static, has_args, has_keywords,
                        doc_str)
        self.__method_list.append(method)

    def add_getter(self, func_name, *,
                   has_closure=False,
                   gen_body):
        """getter 定義を追加する．
        """
        self.__check_name(func_name)
        func_def = FuncDef(func_name, gen_body)
        getset = GetSet(func_def, has_closure)
        self.__getter_list.append(getset)

    def add_setter(self, func_name, *,
                   has_closure=False,
                   gen_body):
        """setter 定義を追加する．
        """
        self.__check_name(func_name)
        func_def = FuncDef(func_name, gen_body)
        getset = GetSet(func_def, has_closure)
        self.__setter_list.append(getset)

    def add_attr(self, name, *,
                 getter_name=None,
                 setter_name=None,
                 closure=None,
                 doc_str):
        """属性定義を追加する．
        """
        if getter_name is None:
            getter_name = 'nullptr'
        else:
            for getter in self.__getter_list:
                if getter.func_def.name == getter_name:
                    # found
                    if closure is None:
                        if getter.has_closure:
                            raise ValueError(f'{getter_name} takes closure argument')
                    else:
                        if not getter.has_closure:
                            raise ValueError(f'{getter_name} takes no closure argument')
                    break
            else:
                # not found
                raise ValueError(f'getter({getter_name}) is not registered')
        if setter_name is None:
            setter_name = 'nullptr'
        else:
            for setter in self.__setter_list:
                if setter.func_def.name == setter_name:
                    # found
                    if closure is None:
                        if setter.has_closure:
                            raise ValueError(f'{setter_name} takes closure argument')
                    else:
                        if not setter.has_closure:
                            raise ValueError(f'{setter_name} takes no closure argument')
                    break
            else:
                # not found
                raise ValueError(f'setter({setter_name}) is not registered')
        if closure is None:
            closure = 'nullptr'
        for attr in self.__attr_list:
            if attr.name == name:
                raise ValueError(f'{name} has already been registered')
        attr = Attr(name, getter_name, setter_name, closure, doc_str)
        self.__attr_list.append(attr)

    def add_conv(self, gen_body=None):
        if gen_body is None:
            # デフォルト実装
            def conv_gen(gen):
                gen._write_line(f'new (&obj1->mVal) {self.classname}(val);')
            gen_body = conv_gen
        self.__conv_gen = gen_body

    def add_deconv(self, gen_body=None):
        if gen_body is None:
            # デフォルト実装
            def deconv_gen(gen):
                with gen.gen_if_block(f'{gen.pyclassname}::Check(obj)'):
                    gen.gen_assign('val', f'{gen.pyclassname}::_get_ref(obj)')
                    gen.gen_return('true')
                gen.gen_return('false')
            gen_body = deconv_gen
        self.__deconv_gen = gen_body
                
    def make_header(self, fout=sys.stdout):
        """ヘッダファイルを出力する．"""

        # テンプレートファイルは同じディレクトリにあると仮定している．
        template_file = self.template_file("PyCustom.h")

        # 結果のヘッダファイル名
        header_file = f'{self.pyclassname}.h'

        # インタロック用マクロ名
        cap_header_file = self.pyclassname.upper()

        self.__fout = fout
        with open(template_file, 'rt') as fin:
            for line in fin:
                # 余分な改行を削除
                line = line.rstrip()

                if line == '%%INCLUDES%%':
                    # インクルードファイルの置換
                    for filename in self.header_include_files:
                        self.gen_include(filename)
                    continue

                result = self.__conv_def_pat.match(line)
                if result:
                    # Conv の宣言
                    self._indent_set(len(result.group(1)))
                    self.conv_def_gen()
                    self._indent_set(0)
                    continue

                result = self.__deconv_def_pat.match(line)
                if result:
                    # Deconv の宣言
                    self._indent_set(len(result.group(1)))
                    self.deconv_def_gen()
                    self._indent_set(0)
                    continue

                result = self.__to_def_pat.match(line)
                if result:
                    # ToPyObject の宣言
                    self._indent_set(len(result.group(1)))
                    self.to_def_gen()
                    self._indent_set(0)
                    continue

                result = self.__from_def_pat.match(line)
                if result:
                    # FromPyObject の宣言
                    self._indent_set(len(result.group(1)))
                    self.from_def_gen()
                    self._indent_set(0)
                    continue
                
                # 年の置換
                line = line.replace('%%Year%%', self.year())
                # インタロック用マクロ名の置換
                line = line.replace('%%PYCUSTOM%%', cap_header_file)
                # クラス名の置換
                line = line.replace('%%Custom%%', self.classname)
                # Python 拡張用のクラス名の置換
                line = line.replace('%%PyCustom%%', self.pyclassname)
                # 名前空間の置換
                line = line.replace('%%NAMESPACE%%', self.namespace)

                self._write_line(line)

    def conv_def_gen(self):
        self.gen_CRLF()
        if self.__conv_gen is None:
            if self.__deconv_gen is None:
                self.gen_comment('このクラスは Conv/Deconv を持たない．')
            else:
                self.gen_comment('このクラスは Conv を持たない．')
        else:
            self.gen_dox_comment(f'@brief {self.classname} を PyObject* に変換するファンクタクラス')
            with self.gen_struct_block('Conv'):
                self.gen_func_declaration(return_type='PyObject*',
                                          func_name='operator()',
                                          args=['const ElemType& val'])

    def deconv_def_gen(self):
        if self.__deconv_gen is None:
            if self.__conv_gen is not None:
                self.gen_CRLF()
                self.gen_comment('このクラスは Deconv を持たない．')
        else:
            self.gen_CRLF()
            self.gen_dox_comment(f'@brief PyObject* から {self.classname} を取り出すファンクタクラス')
            with self.gen_struct_block('Deconv'):
                self.gen_func_declaration(return_type='bool',
                                          func_name='operator()',
                                          args=['PyObject* obj',
                                                'ElemType& val'])

    def to_def_gen(self):
        if self.__conv_gen is not None:
            self.gen_CRLF()
            self.gen_dox_comment(f'@brief {self.classname} を表す PyObject を作る．')
            self.gen_dox_comment('@return 生成した PyObject を返す．')
            self.gen_dox_comment('')
            self.gen_dox_comment('返り値は新しい参照が返される．')
            with self.gen_func_block(is_static=True,
                                     return_type='PyObject*',
                                     func_name='ToPyObject',
                                     args=('const ElemType& val ///< [in] 値', )):
                self.gen_declaration('Conv', 'conv')
                self.gen_return('conv(val)')

    def from_def_gen(self):
        if self.__deconv_gen is not None:
            self.gen_CRLF()
            self.gen_dox_comment(f'@brief PyObject から {self.classname} を取り出す．')
            self.gen_dox_comment('@return 正しく変換できた時に true を返す．')
            with self.gen_func_block(is_static=True,
                                     return_type='bool',
                                     func_name='FromPyObject',
                                     args=('PyObject* obj, ///< [in] Python のオブジェクト',
                                           'ElemType& val  ///< [out] 結果を格納する変数')):
                self.gen_declaration('Deconv', 'deconv')
                self.gen_return('deconv(obj, val)')
                
    def make_source(self, fout=sys.stdout):
        """ソースファイルを出力する．"""
        
        # テンプレートファイルは同じディレクトリにあると仮定している．
        template_file = self.template_file("PyCustom.cc")

        self.__fout = fout
        with open(template_file, 'rt') as fin:
            for line in fin:
                # 余分な改行を削除
                line = line.rstrip()

                if line == '%%INCLUDES%%':
                    # インクルードファイルの置換
                    for filename in self.source_include_files:
                        self.gen_include(filename)
                    continue

                if line == '%%EXTRA_CODE%%':
                    self.make_extra_code()
                    continue

                result = self.__tp_init_pat.match(line)
                if result:
                    # tp_XXX 設定の置換
                    self._indent_set(len(result.group(1)))
                    self.make_tp_init()
                    self._indent_set(0)
                    continue

                result = self.__ex_init_pat.match(line)
                if result and self.__ex_init_gen is not None:
                    # 追加の初期化コードの置換
                    self.indent = len(result.group(1))
                    self.__ex_init_gen()
                    self.indent = 0
                    continue

                if line == '%%CONV_CODE%%':
                    # Conv 関数の置換
                    if self.__conv_gen is not None:
                        self.make_conv()
                    continue

                if line == '%%DECONV_CODE%%':
                    # Deconv 関数の置換
                    if self.__deconv_gen is not None:
                        self.make_deconv()
                    continue
                
                # 年の置換
                line = line.replace('%%Year%%', self.year())
                # クラス名の置換
                line = line.replace('%%Custom%%', self.classname)
                # Python 拡張用のクラス名の置換
                line = line.replace('%%PyCustom%%', self.pyclassname)
                # Python 上のタイプ名の置換
                line = line.replace('%%TypeName%%', self.pyname)
                # 名前空間の置換
                line = line.replace('%%NAMESPACE%%', self.namespace)
                # タイプクラス名の置換
                line = line.replace('%%CustomType%%', self.typename)
                # オブジェクトクラス名の置換
                line = line.replace('%%CustomObject%%', self.objectname)

                self._write_line(line)

    def make_extra_code(self):
        if self.__preamble_gen is not None:
            self.__preamble_gen(self)
        
        if self.__dealloc is not None:
            with self.gen_func_block(description='終了関数',
                                     return_type='void',
                                     func_name=self.__dealloc.name,
                                     args=(('PyObject* self', ))):
                self.gen_obj_conv('obj')
                self.__dealloc.func(self)
                self._write_line('PyTYPE(self)->tp_free(self)')

        if self.__repr is not None:
            with self.gen_func_block(description='repr関数',
                                     return_type='PyObject*',
                                     func_name=self.__repr.name,
                                     args=(('PyObject* self', ))):
                self.gen_val_conv('val')
                self.gen_auto_assign('repr_str', self.__repr.func('val'))
                self.gen_return(f'PyString::ToPyObject(repr_str)')

        if self.number_gen is not None:
            self.number_gen(self.__number_name)

        if self.__sequence_tbl is not None:
            self.gen_sequence()

        if self.mapping_gen is not None:
            self.mapping_gen(self.__mapping_name)

        if self.__hash is not None:
            self.__hash.func(self.__hash.name)

        if self.__str is not None:
            self.__str.func(self.__str.name)

        if self.__richcompare is not None:
            self.__richcompare.func(self.__richcompare.name)

        if len(self.__method_list) > 0:
            self.gen_methods()
            
        if len(self.__attr_list) > 0:
            self.gen_getset()

        if self.__init is not None:
            self.__init.func(self.__init.name)

        if self.__new is not None:
            args = ('PyTypeObject* type',
                    'PyObject* args',
                    'PyObject* kwds')
            with self.gen_func_block(description='生成関数',
                                     return_type='PyObject*',
                                     func_name=self.__new.name,
                                     args=args):
                self.gen_func_preamble(self.__new.arg_list)
                self.__new.func(self)

    def gen_sequence(self):
        length = self.__sequence_tbl.length
        if length is not None:
            args = ('PyObject* self',)
            with self.gen_func_block(return_type='Py_ssize_t',
                                     func_name=length.name,
                                     args=args):
                length.func(self)
        concat = self.__sequence_tbl.concat
        if  concat is not None:
            args = ('PyObject* self',
                    'PyObject* obj2')
            with self.gen_func_block(return_type='PyObject*',
                                     func_name=concat.name,
                                     args=args):
                concat.func(self)
        repeat = self.__sequence_tbl.repeat
        if repeat is not None:
            args = ('PyObject* self',
                    'Py_ssize_t obj2')
            with self.gen_func_block(return_type='PyObject*',
                                     func_name=repeat.name,
                                     args=args):
                repeat.func(self)
        item = self.__sequence_tbl.item
        if item is not None:
            args = ('PyObject* self',
                    'Py_ssize_t obj2')
            with self.gen_func_block(return_type='PyObject*',
                                     func_name=item.name,
                                     args=args):
                item.func(self)
        ass_item = self.__sequence_tbl.ass_item
        if ass_item is not None:
            args = ('PyObject* self',
                    'Py_ssize_t obj2',
                    'PyObject* obj3')
            with self.gen_func_block(return_type='int',
                                     func_name=ass_item.name,
                                     args=args):
                ass_item.func(self)
        contains = self.__sequence_tbl.contains
        if contains is not None:
            args = ('PyObject* self',
                    'PyObject* obj2')
            with self.gen_func_block(return_type='int',
                                     func_name=contains.name,
                                     args=args):
                contains.func(self)
        inplace_concat = self.__sequence_tbl.inplace_concat
        if inplace_concat is not None:
            args = ('PyObject* self',
                    'PyObject* obj2')
            with self.gen_func_block(return_type='PyObject*',
                                     func_name=inplace_concat.name,
                                     args=args):
                inplace_concat.func(self)
        inplace_repeat = self.__sequence_tbl.inplace_repeat
        if inplace_repeat is not None:
            args = ('PyObject* self',
                    'Py_ssize_t obj2')
            with self.gen_func_block(return_type='PyObject*',
                                     func_name=inplace_repeat.name,
                                     args=args):
                inplace_repeat.func(self)
            
        self.gen_CRLF()
        self.gen_comment('シーケンスオブジェクト構造体')
        with self.gen_array_block(typename='PySequenceMethods',
                                  arrayname=self.__sequence_name):
            line = None
            length = self.__sequence_tbl.length
            if length is not None:
                if line is not None:
                    line += ','
                    self._write_line(line)
                line = f'.sq_length = {length.name}'
            concat = self.__sequence_tbl.concat
            if concat is not None:
                if line is not None:
                    line += ','
                    self._write_line(line)
                line = f'.sq_concat = {concat.name}'
            repeat = self.__sequence_tbl.repeat
            if repeat is not None:
                if line is not None:
                    line += ','
                    self._write_line(line)
                line = f'.sq_repeat = {repeat.name}'
            item = self.__sequence_tbl.item
            if item is not None:
                if line is not None:
                    line += ','
                    self._write_line(line)
                line = f'.sq_item = {item.name}'
            ass_item = self.__sequence_tbl.ass_item
            if ass_item is not None:
                if line is not None:
                    line += ','
                    self._write_line(line)
                line = f'.sq_ass_item = {ass_item.name}'
            contains = self.__sequence_tbl.contains
            if contains is not None:
                if line is not None:
                    line += ','
                    self._write_line(line)
                line = f'.sq_contains = {contains.name}'
            inplace_concat = self.__sequence_tbl.inplace_concat
            if inplace_concat is not None:
                if line is not None:
                    line += ','
                    self._write_line(line)
                line = f'.sq_inplace_concat = {inplace_concat.name}'
            inplace_repeat = self.__sequence_tbl.inplace_repeat
            if inplace_repeat is not None:
                if line is not None:
                    line += ','
                    self._write_line(line)
                line = f'.sq_inplace_repeat = {inplace_repeat.name}'
            self._write_line(line)
    
    def gen_methods(self):
        for method in self.__method_list:
            if method.is_static:
                arg0 = 'PyObject* Py_UNUSED(self)'
            else:
                arg0 = 'PyObject* self'
            if method.has_args:
                arg1 = 'PyObject* args'
            else:
                arg1 = 'PyObject* Py_UNUSED(args)'
            if method.has_keywords:
                arg2 = 'PyObject* kwds'
                args = [ arg0, arg1, arg2 ]
            else:
                args = [ arg0, arg1 ]
            with self.gen_func_block(description=method.doc_str,
                                     return_type='PyObject*',
                                     func_name=method.func_def.name,
                                     args=args):
                self.gen_func_preamble(method.func_def.arg_list)
                method.func_def.func(self)

        self.gen_CRLF()
        self.gen_comment('メソッド定義')
        with self.gen_array_block(typename='PyMethodDef',
                                  arrayname=self.__method_name):
            for method in self.__method_list:
                self._write_line(f'{{"{method.name}",')
                self._indent_inc(1)
                line = ''
                if method.has_keywords:
                    line = 'reinterpret_cast<PyCFunction>('
                line += method.func_def.name
                if method.has_keywords:
                    line += ')'
                line += ','
                self._write_line(line)
                if method.has_args:
                    line = 'METH_VARARGS'
                    if method.has_keywords:
                        line += ' | METH_KEYWORDS'
                else:
                    line = 'METH_NOARGS'
                if method.is_static:
                    line += ' | METH_STATIC'
                line += ','
                self._write_line(line)
                line = f'PyDoc_STR("{method.doc_str}")}},'
                self._write_line(line)
                self._indent_dec(1)
            self.gen_comment('end-marker')
            self._write_line('{nullptr, nullptr, 0, nullptr}')

    def gen_getset(self):
        # getter 関数の生成
        for func_def, has_closure in self.__getter_list:
            arg0 = 'PyObject* self'
            if has_closure:
                arg1 = 'void* closure'
            else:
                arg1 = 'void* Py_UNUSED(closure)'
            args = [ arg0, arg1 ]
            with self.gen_func_block(return_type='PyObject*',
                                     func_name=func_def.name,
                                     args=args):
                self.gen_val_conv('val')
                func_def.func(self)
                
        # setter 関数の生成
        for func_def, has_closure in self.__setter_list:
            arg0 = 'PyObject* self'
            arg1 = 'PyObject* obj'
            if has_closure:
                arg2 = 'void* closure'
            else:
                arg2 = 'void* Py_UNUSED(closure)'
            args = [ arg0, arg1, arg2 ]
            with self.gen_func_block(return_type='int',
                                     func_name=func_def.name,
                                     args=args):
                self.gen_val_conv('val')
                func_def.func(self)

        # getset テーブルの生成
        self.gen_CRLF()
        self.gen_comment('getter/setter定義')
        with self.gen_array_block(typename='PyGetSetDef',
                                  arrayname=self.__getset_name):
            for attr in self.__attr_list:
                line = f'{{"{attr.name}", {attr.getter_name}, {attr.setter_name}, PyDoc_STR("{attr.doc_str}"), {attr.closure}}},'
                self._write_line(line)
                self.gen_comment('end-marker')
                self._write_line('{nullptr, nullptr, nullptr, nullptr}')
                
    def make_tp_init(self):
        tp_list = []
        tp_list.append(('name', f'"{self.pyname}"'))
        tp_list.append(('basicsize', f'sizeof({self.objectname})'))
        tp_list.append(('itemsize', '0'))
        if self.__dealloc is not None:
            tp_list.append(('dealloc', f'{self.__dealloc.name}'))
        if self.__repr is not None:
            tp_list.append(('repr', f'{self.__repr.name}'))
        if self.__number_name is not None:
            tp_list.append(('as_number', f'{self.__number_name}'))
        if self.__sequence_name is not None:
            tp_list.append(('as_sequence', f'{self.__sequence_name}'))
        if self.__mapping_name is not None:
            tp_list.append(('as_mapping', f'{self.__mapping_name}'))
        if self.__hash is not None:
            tp_list.append(('hash', f'{self.__hash.name}'))
        if self.__call is not None:
            tp_list.append(('call', f'{self.__call.name}'))
        if self.__str is not None:
            tp_list.append(('str', f'{self.__str.name}'))
        tp_list.append(('flags', 'Py_TPFLAGS_DEFAULT'))
        tp_list.append(('doc', f'PyDoc_STR("{self.doc_str}")'))
        if self.__richcompare is not None:
            tp_list.append(('richcompare', f'{self.__richcompare.name}'))
        if len(self.__method_list) > 0:
            tp_list.append(('methods', f'{self.__method_name}'))
        if len(self.__attr_list) > 0:
            tp_list.append(('getset', f'{self.__getset_name}'))
        if self.__init is not None:
            tp_list.append(('init', f'{self.__init.name}'))
        if self.__new is not None:
            tp_list.append(('new', f'{self.__new.name}'))
        for name, rval in tp_list:
            self.gen_assign(f'{self.typename}.tp_{name}', f'{rval}')

    def make_conv(self):
        description = f'{self.classname} を PyObject に変換する．'
        with self.gen_func_block(description=description,
                                 return_type='PyObject*',
                                 func_name=f'{self.pyclassname}::Conv::operator()',
                                 args=(f'const {self.classname}& val', )):
            self.gen_auto_assign('type', f'{self.pyclassname}::_typeobject()')
            self.gen_auto_assign('obj', 'type->tp_alloc(type, 0)')
            self.gen_auto_assign('obj1', f'reinterpret_cast<{self.objectname}*>(obj)')
            self.__conv_gen(self)
            self.gen_return('obj')

    def make_deconv(self,):
        description = f'PyObject を {self.classname} に変換する．'
        with self.gen_func_block(description=description,
                                 return_type='bool',
                                 func_name=f'{self.pyclassname}::Deconv::operator()',
                                 args=('PyObject* obj',
                                       f'{self.classname}& val')):
            self.__deconv_gen(self)
            
    def __complete(self, func_def, default_name):
        """名前がない場合に名前を補完する．

        新しい FuncDef を返す．
        """
        if func_def is None:
            return None
        name = func_def.name
        if name is None:
            name = default_name
        self.__check_name(name)
        return FuncDef(name, func_def.func)

    def __check_name(self, name):
        """名前が重複していないかチェックする．

        重複していたら例外を送出する．
        """
        if name in self.__name_dict:
            raise ValueError(f'{name} is already in use')
        self.__name_dict.add(name)
        return name

    @staticmethod
    def year():
        """現在の年を表す文字列を返す．
        """
        return str(datetime.datetime.now().year)

    @staticmethod
    def template_file(filename):
        """テンプレートファイル名を返す．
        """
        basedir = os.path.dirname(__file__)
        return os.path.join(basedir, filename)

    def gen_func_preamble(self, arg_list):
        """引数を解釈する前処理のコードを生成する．
        """
        has_args, has_keywords = analyze_args(arg_list)
        if has_keywords:
            # キーワードテーブルの定義
            kwds_table = 'kwlist'
            with self.gen_array_block(typename='static const char*',
                                      arrayname=kwds_table):
                for arg in arg_list:
                    if arg.name is None:
                        self._write_line('"",')
                    else:
                        self._write_line(f'"{arg.name}",')
                self._write_line('nullptr')

        # パーズ結果を格納する変数の宣言
        for arg in arg_list:
            arg.gen_vardef()

        # PyArg_Parse() 用のフォーマット文字列の生成
        fmt_str = ""
        mode = "init" # init|option|keyword の3つ
        for arg in arg_list:
            if arg.option:
                if mode == "init":
                    fmt_str += "|"
                    mode = "option"
            if arg.name is None:
                if mode == "keyword":
                    raise ValueError('nameless argument is not allowed here')
            else:
                if mode == "option":
                    fmt_str += "$"
                    mode = "keyword"
            fmt_str += f'{arg.pchar}'
                    
        # パーズ関数の呼び出し
        if has_args:
            if has_keywords:
                line = f'if ( !PyArg_ParseTupleAndKeywords(args, kwds, "{fmt_str}",'
                self._write_line(line)
                fpos = line.find('(')
                delta = line.find('(', fpos + 1) + 1
                self._indent_inc(delta)
                self._write_line(f'const_cast<char**>({kwds_table}),')
            else:
                line = f'if ( !PyArg_Parse(args, "{fmt_str}",'
                fpos = line.find('(')
                delta = line.find('(', fpos + 1) + 1
            nargs = len(arg_list)
            for i, arg in enumerate(arg_list):
                line = arg.gen_varref()
                if i < nargs - 1:
                    line += ','
                else:
                    line += ') ) {'
                self._write_line(line)
            self._indent_dec(delta)
            self._indent_inc()
            self.gen_return('nullptr')
            self._indent_dec()
            self._write_line('}')

        # PyObject から C++ の変数へ変換する．
        for arg in arg_list:
            arg.gen_conv()

    def gen_include(self, filename, *,
                    sysinclude=False):
        """include 文を出力する．
        """
        line = '#include '
        if sysinclude:
            line += '<'
        else:
            line += '"'
        line += filename
        if sysinclude:
            line += '>'
        else:
            line += '"'
        self._write_line(line)

    def gen_obj_conv(self, varname):
        """self から自分の型に変換するコードを生成する．
        """
        self.gen_auto_assign(f'{varname}',
                             f'reinterpret_cast<{self.objectname}*>(self)')

    def gen_val_conv(self, varname):
        """self から値を取り出すコードを生成する．
        """
        self.gen_assign(f'auto& {varname}',
                        f'{self.pyclassname}::_get_ref(self)')

    def gen_declaration(self, typename, varname):
        """変数宣言を出力する．
        """
        self._write_line(f'{typename} {varname};')
        
    def gen_auto_assign(self, lval, rval):
        """auto 宣言付きの代入文を出力する．
        """
        self.gen_assign(lval, rval, autodef=True)
        
    def gen_assign(self, lval, rval, *,
                   autodef=False):
        """代入文を出力する．
        """
        if autodef:
            line = 'auto '
        else:
            line = ''
        line += f'{lval} = {rval};'
        self._write_line(line)

    def gen_buildvalue_return(self, fmt, val_list):
        """ Py_BuildValue() を用いた return 文を出力する．
        """
        line = f'return Py_BuildValue("{fmt}"'
        for val in val_list:
            line += f', {val}'
        line += ';'
        self._write_line(line)
        
    def gen_return(self, val):
        """return 文を出力する．
        """
        line = 'return'
        if val is not None:
            line += f' {val}'
        line += ';'
        self._write_line(line)

    def gen_return_py_int(self, varname):
        """int 値を表す PyObject を返す return 文を出力する．
        """
        self.gen_return(f'Py_BuildValue("i", {varname})')

    def gen_return_py_float(self, varname):
        """float 値を表す PyObject を返す return 文を出力する．
        """
        self.gen_return(f'Py_BuildValue("d", {varname})')

    def gen_return_py_string(self, varname):
        """string 値を表す PyObject を返す return 文を出力する．
        """
        self.gen_return(f'Py_BuildValue("s", {varname})')

    def gen_return_py_bool(self, varname):
        """bool 値を表す PyObject を返す return 文を出力する．
        """
        self.gen_return(f'PyBool_FromLong({varname})')
        
    def gen_return_py_none(self):
        """Py_RETURN_NONE を出力する．
        """
        self._write_line('Py_RETURN_NONE;')
        
    def gen_func_declaration(self, *,
                             description=None,
                             is_static=False,
                             return_type,
                             func_name,
                             args):
        """関数宣言を出力する．
        """
        self.gen_func_header(description=description,
                             is_static=is_static,
                             is_declaration=True,
                             return_type=return_type,
                             func_name=func_name,
                             args=args)

    def gen_func_header(self, *,
                        description=None,
                        is_static=False,
                        is_declaration,
                        return_type,
                        func_name,
                        args):
        """関数ヘッダを出力する．
        """
        self.gen_CRLF()
        if description is not None:
            self.gen_comment(f'@brief {description}')
        if is_static:
            self._write_line('static')
        self._write_line(f'{return_type}')
        if is_declaration:
            postfix=';'
        else:
            postfix=''
        with CodeBlock(self,
                       br_chars='()',
                       prefix=func_name,
                       postfix=postfix):
            nargs = len(args)
            for i, arg in enumerate(args):
                line = arg
                if i < nargs - 1:
                    line += ','
                self._write_line(line)
                        
    def gen_func_block(self, *,
                       description=None,
                       is_static=False,
                       return_type,
                       func_name,
                       args):
        """関数定義を出力する．

        with obj.gen_func_block(return_type=XX,
                                func_name=XX,
                                args=..):
          ...
        という風に用いる．
        """
        return FuncBlock(self,
                         description=description,
                         is_static=is_static,
                         return_type=return_type,
                         func_name=func_name,
                         args=args)
                       
    def gen_if_block(self, condition):
        """if 文を出力する

        with obj.gen_if_block(condition):
          ...
        という風に用いる．
        """
        return IfBlock(self, condition)

    def gen_else_block(self):
        """else文を出力する

        with obj.gen_else_block():
          ...
        という風に用いる．
        """
        return ElseBlock(self)

    def gen_elseif_block(self, condition):
        """else if 文を出力する

        with obj.gen_elseif_block(condition):
          ...
        という風に用いる．
        """
        return ElseIfBlock(self, condition)

    def gen_for_block(self,
                      init_stmt,
                      cond_expr,
                      next_stmt):
        """for 文を出力する．
        """
        return ForBlock(self, init_stmt, cond_expr, next_stmt)

    def gen_array_block(self, *,
                        typename,
                        arrayname):
        """initializer を持つ配列定義用ブロックを出力する．
        """
        return ArrayBlock(self, typename=typename, arrayname=arrayname)

    def gen_struct_block(self, structname):
        """struct ブロックを出力する．
        """
        return StructBlock(self, structname)

    def gen_try_block(self):
        """try ブロックを出力する．
        """
        return TryBlock(self)

    def gen_catch_block(self, expr):
        """catch ブロックを出力する．
        """
        return CatchBlock(self, expr)
    
    def gen_type_error(self, error_msg, *, noexit=False):
        self.gen_error('PyExc_TypeError', error_msg, noexit=noexit)

    def gen_value_error(self, error_msg, *, noexit=False):
        self.gen_error('PyExc_ValueError', error_msg, noexit=noexit)
        
    def gen_error(self, error_type, error_msg, *, noexit=False):
        """エラー出力
        """
        self._write_line(f'PyErr_SetString({error_type}, {error_msg});')
        if not noexit:
            self.gen_return('nullptr')
        
    def gen_dox_comment(self, comment):
        """Doxygen 用のコメントを出力する．
        """
        self.gen_comment(comment, doxygen=True)

    def gen_comment(self, comment, *, doxygen=False):
        """コメントを出力する．
        """
        if doxygen:
            line = '///'
        else:
            line = '//'
        line += f' {comment}'
        self._write_line(line)
        
    def gen_CRLF(self):
        """空行を出力する．
        """
        self._write_line('')
        
    def _write_line(self, line):
        spc = ' ' * self.__indent
        self.__fout.write(f'{spc}{line}\n')

    def _indent_inc(self, delta=2):
        self.__indent += delta

    def _indent_dec(self, delta=2):
        self.__indent -= delta

    def _indent_set(self, val):
        self.__indent = val
    
                
if __name__ == '__main__':
    from argparse import ArgumentParser
    from mk_py_capi import MethodGen

    parser = ArgumentParser(
        prog='mk_source',
        description='make source file for Python extention')
    parser.add_argument('classname')
    parser.add_argument('namespace')
    parser.add_argument('--include_file', nargs='*', type=str)

    args = parser.parse_args()

    classname = args.classname
    pyclassname = 'Py' + classname
    pyname = classname
    namespace = args.namespace
    if args.include_file is None:
        include_files = [f'{classname}.h']
    else:
        include_files = args.include_file

    make_source = MkSource(classname=classname,
                           pyclassname=pyclassname,
                           namespace=namespace,
                           pyname=pyname,
                           include_files=include_files)

    make_source.dealloc_gen = DeallocGen(make_source)
    make_source.conv_gen = ConvGen(make_source)
    make_source.deconv_gen = DeconvGen(make_source)

    class NullMethod(MethodGen):

        def __init__(self, parent):
            super().__init__(parent,
                             name='null',
                             func_name='null',
                             has_args=False,
                             has_keywords=False,
                             is_static=True,
                             doc_str='make Null object')

        def bodygen(self):
            self._write_line(f'return {self.pyclassname}::ToPyObject(JsonValue::null());')

    make_source.add_method(NullMethod(make_source))
    
    make_source()
            
