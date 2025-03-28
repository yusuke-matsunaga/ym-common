#! /usr/bin/env python3

""" MkPyCapi のクラス定義ファイル

:file: mk_py_capi.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from .codegen import CodeGen
from .number_gen import NumberGen
from .sequence_gen import SequenceGen
from .mapping_gen import MappingGen
from .method_gen import MethodGen
from .getset_gen import GetSetGen
from .utils import FuncDef, FuncDefWithArgs
from .utils import analyze_args
from .cxxwriter import CxxWriter
import re
import os
import datetime
import sys


class MkPyCapi(CodeGen):
    """Python 拡張用のヘッダ/ソースファイルを生成するためのクラス
    """

    def __new__(cls, *,
                classname,
                pyclassname=None,
                namespace=None,
                typename=None,
                objectname=None,
                pyname,
                header_include_files=[],
                source_include_files=[]):
        self = super().__new__(cls,
                               classname=classname,
                               pyclassname=pyclassname,
                               namespace=namespace,
                               typename=typename,
                               objectname=objectname,
                               pyname=pyname)
        return self
    
    def __init__(self, *,
                 classname,
                 pyclassname=None,
                 namespace=None,
                 typename=None,
                 objectname=None,
                 pyname,
                 header_include_files=[],
                 source_include_files=[]):

        # ヘッダファイル用のインクルードファイルリスト
        self.header_include_files = header_include_files
        # ソースファイル用のインクルードファイルリスト
        self.source_include_files = source_include_files

        # 出力するC++の変数名の重複チェック用の辞書
        self.__name_dict = set()

        # プリアンブル出力器
        self.__preamble_gen = None

        # 組み込み関数生成器
        self.__dealloc_def = None
        self.__repr_def = None
        self.__hash_def = None
        self.__call_def = None
        self.__str_def = None
        self.__richcompare_def = None
        self.__init_def = None
        self.__new_def = None

        # Number 構造体の定義
        self.__number_name = None
        self.__number_gen = None

        # Sequence 構造体の定義
        self.__sequence_name = None
        self.__sequence_gen = None

        # Mapping 構造体の定義
        self.__mapping_name = None
        self.__mapping_gen = None

        # メソッド構造体の定義
        self.__method_name = self.__check_name('method')
        self.__method_gen = MethodGen()

        # get/set 構造体の定義
        self.__getset_name = self.__check_name('getset')
        self.__getset_gen = GetSetGen()

        # 追加の初期化コード
        self.__ex_init_gen = None

        # PyObject への変換を行うコード
        self.__conv_gen = None

        # PyObject からの逆変換を行うコード
        self.__deconv_gen = None

        self.basicsize = f'sizeof({self.objectname})'
        self.itemsize = '0'
        self.flags = 'Py_TPFLAGS_DEFAULT'
        
        # 説明文
        self.doc_str = f'{self.classname} object'

        # 置換用のパタン
        # 字下げ位置を求めるために正規表現を用いている．
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
                    dealloc_func=None):
        """dealloc 関数定義を追加する．
        """
        if self.__dealloc_def is not None:
            raise ValueError('dealloc has been already defined')
        func_name = self.__complete(func_name, 'dealloc_func')
        if dealloc_func is None:
            # デフォルト実装
            def default_func(writer):
                writer.write_line(f'obj->mVal.~{self.classname}()')
            dealloc_func = default_func
        def dealloc_body(writer):
            writer.gen_obj_conv(varname='obj')
            dealloc_func(writer)
            writer.write_line('PyTYPE(self)->tp_free(self)')
        self.__dealloc_def = FuncDef(func_name, dealloc_body)

    def add_repr(self, *,
                 func_name=None,
                 repr_func):
        """repr 関数定義を追加する．
        """
        if self.__repr_def is not None:
            raise ValueError('repr has been already defined')
        func_name = self.__complete(func_name, 'repr_func')
        def repr_body(writer):
            writer.gen_ref_conv(refname='val')
            writer.gen_auto_assign('str_val', repr_func('val'))
            writer.gen_return_py_string('str_val')
        self.__repr_def = FuncDef(func_name, repr_body)

    def add_number(self, *,
                   name=None,
                   nb_add=None,
                   nb_subtract=None,
                   nb_multiply=None,
                   nb_remainder=None,
                   nb_dvmod=None,
                   nb_power=None,
                   nb_negative=None,
                   nb_positive=None,
                   nb_absolute=None,
                   nb_bool=None,
                   nb_invert=None,
                   nb_lshift=None,
                   nb_rshift=None,
                   nb_and=None,
                   nb_xor=None,
                   nb_or=None,
                   nb_int=None,
                   nb_float=None,
                   nb_inplace_add=None,
                   nb_inplace_subtract=None,
                   nb_inplace_multiply=None,
                   nb_inplace_remainder=None,
                   nb_inplace_power=None,
                   nb_inplace_lshft=None,
                   nb_inplace_rshift=None,
                   nb_inplace_and=None,
                   nb_inplace_xor=None,
                   nb_inplace_or=None,
                   nb_floor_divide=None,
                   nb_true_divide=None,
                   nb_inplace_floor_divide=None,
                   nb_inplace_true_divide=None,
                   nb_index=None,
                   nb_matrix_multiply=None,
                   nb_inplace_matrix_multiply=None):
        """Number オブジェクト構造体を定義する．
        """
        if self.__number_gen is not None:
            raise ValueError('number has been already defined')
        self.__number_name = self.__complete(name, 'number')
        self.__number_gen = NumberGen(
            nb_add=self.__complete_funcdef(nb_add, 'nb_add'),
            nb_subtract=self.__complete_funcdef(nb_subtract, 'nb_subtract'),
            nb_multiply=self.__complete_funcdef(nb_multiply, 'nb_multiply'),
            nb_remainder=self.__complete_funcdef(nb_remainder, 'nb_remainder'),
            nb_divmod=self.__complete_funcdef(nb_divmod, 'nb_divmod'),
            nb_power=self.__complete_funcdef(nb_power, 'nb_power'),
            nb_negative=self.__complete_funcdef(nb_negative, 'nb_negative'),
            nb_positive=self.__complete_funcdef(nb_positive, 'nb_positive'),
            nb_absolute=self.__complete_funcdef(nb_absolute, 'nb_absolute'),
            nb_bool=self.__complete_funcdef(nb_bool, 'nb_bool'),
            nb_invert=self.__complete_funcdef(nb_invert, 'nb_invert'),
            nb_lshift=self.__complete_funcdef(nb_lshift, 'nb_lshift'),
            nb_rshift=self.__complete_funcdef(nb_rshift, 'nb_rshift'),
            nb_and=self.__complete_funcdef(nb_and, 'nb_and'),
            nb_xor=self.__complete_funcdef(nb_xor, 'nb_xor'),
            nb_or=self.__complete_funcdef(nb_or, 'nb_or'),
            nb_int=self.__complete_funcdef(nb_int, 'nb_int'),
            nb_float=self.__complete_funcdef(nb_float, 'nb_float'),
            nb_inplace_add=self.__complete_funcdef(nb_inplace_add,
                                                   'nb_inplace_add'),
            nb_inplace_subtract=self.__complete_funcdef(nb_subtract,
                                                        'nb_inplace_subtract'),
            nb_inplace_multiply=self.__complete_funcdef(nb_inplace_multiply,
                                                        'nb_multiply'),
            nb_inplace_remainder=self.__complete_funcdef(nb_inplace_remainder,
                                                         'nb_remainder'),
            nb_inplace_power=self.__complete_funcdef(nb_inplace_power,
                                                     'nb_inplace_power'),
            nb_inplace_lshift=self.__complete_funcdef(nb_inplace_lshift,
                                                      'nb_inplace_lshift'),
            nb_inplace_rshift=self.__complete_funcdef(nb_inplace_rshift,
                                                      'nb_inplace_rshift'),
            nb_inplace_and=self.__complete_funcdef(nb_inplace_and,
                                                   'nb_inplace_and'),
            nb_inplace_xor=self.__complete_funcdef(nb_inplace_xor,
                                                   'nb_inplace_xor'),
            nb_inplace_or=self.__complete_funcdef(nb_inplace_or,
                                                  'nb_inplace_or'),
            nb_index=self.__complete_funcdef(nb_index, 'nb_index'),
            nb_matrix_multiply=self.__complete_funcdef(nb_matrix_multiply,
                                                       'nb_matrix_multiply'),
            nb_inplace_matrix_multiply=self.__complete_funcdef(nb_inplace_matrix_multiply, 'nb_inplace_matrix_multiply')
            )
        
    def add_sequence(self, *,
                     name=None,
                     sq_length=None,
                     sq_concat=None,
                     sq_repeat=None,
                     sq_item=None,
                     sq_ass_item=None,
                     sq_contains=None,
                     sq_inplace_concat=None,
                     sq_inplace_repeat=None):
        """Sequence オブジェクト構造体を定義する．
        """
        if self.__sequence_gen is not None:
            raise ValueError('sequence has been already defined')
        self.__sequence_name = self.__complete(name, 'sequence')
        self.__sequence_gen = SequenceGen(
            sq_length=self.__complete_funcdef(sq_length, 'sq_length'),
            sq_concat=self.__complete_funcdef(sq_concat, 'sq_concat'),
            sq_repeat=self.__complete_funcdef(sq_repeat, 'sq_repeat'),
            sq_item=self.__complete_funcdef(sq_item, 'sq_item'),
            sq_ass_item=self.__complete_funcdef(sq_ass_item, 'sq_ass_item'),
            sq_contains=self.__complete_funcdef(sq_contains, 'sq_contains'),
            sq_inplace_concat=self.__complete_funcdef(sq_inplace_concat,
                                                      'sq_inplace_concat'),
            sq_inplace_repeat=self.__complete_funcdef(sq_inplace_repeat,
                                                      'sq_inplace_repeat'),
            )

    def add_mapping(self, *,
                    name=None,
                    mp_length=None,
                    mp_subscript=None,
                    mp_ass_subscript=None):
        """Mapping オブジェクト構造体を定義する．
        """
        if self.__mapping_gen is not None:
            raise ValueError('mapping has been already defined')
        self.__mapping_name = self.__complete(name, 'mapping')
        self.__mapping_gen = MappingGen(
            mp_length=self.__complete_funcdef(mp_length, 'mp_length'),
            mp_subscript=self.__omplete_funcdef(mp_subscript, 'mp_subscript'),
            mp_ass_subscript=self.__complete_funcdef(mp_ass_subscript, 'mp_ass_subscript')
            )
        
    def add_new(self, *,
                func_name=None,
                arg_list=[],
                gen_body):
        """new 関数定義を追加する．
        """
        if self.__new_def is not None:
            raise ValueError('new has been already defined')
        func_name = self.__complete(func_name, 'new_func')
        self.__new_def = FuncDefWithArgs(func_name, gen_body, arg_list)
        
    def add_method(self, name, *,
                   func_name=None,
                   arg_list=[],
                   is_static=False,
                   gen_body,
                   doc_str=''):
        """メソッド定義を追加する．
        """
        # デフォルトの関数名は Python のメソッド名をそのまま用いる．
        func_name = self.__complete(func_name, name)
        func_def = FuncDefWithArgs(func_name, gen_body, arg_list)
        has_args, has_keywords = analyze_args(arg_list)
        self.__method_gen.add(name=name,
                              func_def=func_def,
                              is_static=is_static,
                              has_args=has_args,
                              has_keywords=has_keywords,
                              doc_str=doc_str)

    def add_getter(self, func_name, *,
                   has_closure=False,
                   gen_body):
        """getter 定義を追加する．
        """
        self.__check_name(func_name)
        self.__getset_gen.add_getter(func_name,
                                     has_closure=has_closure,
                                     gen_body=gen_body)

    def add_setter(self, func_name, *,
                   has_closure=False,
                   gen_body):
        """setter 定義を追加する．
        """
        self.__check_name(func_name)
        self.__getset_gen.add_setter(func_name,
                                     has_closure=has_closure,
                                     gen_body=gen_body)

    def add_attr(self, name, *,
                 getter_name=None,
                 setter_name=None,
                 closure=None,
                 doc_str):
        """属性定義を追加する．
        """
        self.__getset_gen.add_attr(name,
                                   getter_name=getter_name,
                                   setter_name=setter_name,
                                   closure=closure,
                                   doc_str=doc_str)

    def add_conv(self, gen_body=None):
        if gen_body is None:
            # デフォルト実装
            def conv_gen(writer):
                writer.write_line(f'new (&obj1->mVal) {self.classname}(val);')
            gen_body = conv_gen
        self.__conv_gen = gen_body

    def add_deconv(self, gen_body=None):
        if gen_body is None:
            # デフォルト実装
            def deconv_gen(writer):
                with writer.gen_if_block(f'{gen.pyclassname}::Check(obj)'):
                    writer.gen_assign('val', f'{gen.pyclassname}::_get_ref(obj)')
                    writer.gen_return('true')
                writer.gen_return('false')
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

        writer = CxxWriter(self.core_info(), fout=fout)
        with open(template_file, 'rt') as fin:
            for line in fin:
                # 余分な改行を削除
                line = line.rstrip()

                if line == '%%INCLUDES%%':
                    # インクルードファイルの置換
                    for filename in self.header_include_files:
                        writer.gen_include(filename)
                    continue

                result = self.__conv_def_pat.match(line)
                if result:
                    # Conv の宣言
                    writer.indent_set(len(result.group(1)))
                    self.conv_def_gen(writer)
                    writer.indent_set(0)
                    continue

                result = self.__deconv_def_pat.match(line)
                if result:
                    # Deconv の宣言
                    writer.indent_set(len(result.group(1)))
                    self.deconv_def_gen(writer)
                    writer.indent_set(0)
                    continue

                result = self.__to_def_pat.match(line)
                if result:
                    # ToPyObject の宣言
                    writer.indent_set(len(result.group(1)))
                    self.to_def_gen(writer)
                    writer.indent_set(0)
                    continue

                result = self.__from_def_pat.match(line)
                if result:
                    # FromPyObject の宣言
                    writer.indent_set(len(result.group(1)))
                    self.from_def_gen(writer)
                    writer.indent_set(0)
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

                writer.write_line(line)

    def conv_def_gen(self, writer):
        writer.gen_CRLF()
        if self.__conv_gen is None:
            if self.__deconv_gen is None:
                writer.gen_comment('このクラスは Conv/Deconv を持たない．')
            else:
                writer.gen_comment('このクラスは Conv を持たない．')
        else:
            writer.gen_dox_comment(f'@brief {self.classname} を PyObject* に変換するファンクタクラス')
            with writer.gen_struct_block('Conv'):
                writer.gen_func_declaration(return_type='PyObject*',
                                            func_name='operator()',
                                            args=['const ElemType& val'])

    def deconv_def_gen(self, writer):
        if self.__deconv_gen is None:
            if self.__conv_gen is not None:
                writer.gen_CRLF()
                writer.gen_comment('このクラスは Deconv を持たない．')
        else:
            writer.gen_CRLF()
            writer.gen_dox_comment(f'@brief PyObject* から {self.classname} を取り出すファンクタクラス')
            with writer.gen_struct_block('Deconv'):
                writer.gen_func_declaration(return_type='bool',
                                            func_name='operator()',
                                            args=['PyObject* obj',
                                                  'ElemType& val'])
                
    def to_def_gen(self, writer):
        if self.__conv_gen is not None:
            writer.gen_CRLF()
            writer.gen_dox_comment(f'@brief {self.classname} を表す PyObject を作る．')
            writer.gen_dox_comment('@return 生成した PyObject を返す．')
            writer.gen_dox_comment('')
            writer.gen_dox_comment('返り値は新しい参照が返される．')
            with writer.gen_func_block(is_static=True,
                                       return_type='PyObject*',
                                       func_name='ToPyObject',
                                       args=('const ElemType& val ///< [in] 値', )):
                writer.gen_vardecl(typename='Conv',
                                   varname='conv')
                writer.gen_return('conv(val)')

    def from_def_gen(self, writer):
        if self.__deconv_gen is not None:
            writer.gen_CRLF()
            writer.gen_dox_comment(f'@brief PyObject から {self.classname} を取り出す．')
            writer.gen_dox_comment('@return 正しく変換できた時に true を返す．')
            with writer.gen_func_block(is_static=True,
                                       return_type='bool',
                                       func_name='FromPyObject',
                                       args=('PyObject* obj, ///< [in] Python のオブジェクト',
                                             'ElemType& val  ///< [out] 結果を格納する変数')):
                writer.gen_vardecl(typename='Deconv',
                                   varname='deconv')
                writer.gen_return('deconv(obj, val)')
                
    def make_source(self, fout=sys.stdout):
        """ソースファイルを出力する．"""
        
        # テンプレートファイルは同じディレクトリにあると仮定している．
        template_file = self.template_file("PyCustom.cc")

        writer = CxxWriter(self.core_info(), fout=fout)
        with open(template_file, 'rt') as fin:
            for line in fin:
                # 余分な改行を削除
                line = line.rstrip()

                if line == '%%INCLUDES%%':
                    # インクルードファイルの置換
                    for filename in self.source_include_files:
                        writer.gen_include(filename)
                    continue

                if line == '%%EXTRA_CODE%%':
                    self.make_extra_code(writer)
                    continue

                result = self.__tp_init_pat.match(line)
                if result:
                    # tp_XXX 設定の置換
                    writer.indent_set(len(result.group(1)))
                    self.make_tp_init(writer)
                    writer.indent_set(0)
                    continue

                result = self.__ex_init_pat.match(line)
                if result:
                    # 追加の初期化コードの置換
                    if self.__ex_init_gen is not None:
                        writer.indent_set(len(result.group(1)))
                        self.__ex_init_gen(writer)
                        writer.indent_set(0)
                    continue

                if line == '%%CONV_CODE%%':
                    # Conv 関数の置換
                    if self.__conv_gen is not None:
                        self.make_conv(writer)
                    continue

                if line == '%%DECONV_CODE%%':
                    # Deconv 関数の置換
                    if self.__deconv_gen is not None:
                        self.make_deconv(writer)
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

                writer.write_line(line)

    def make_extra_code(self, writer):
        if self.__preamble_gen is not None:
            self.__preamble_gen(writer)
        
        writer.gen_dealloc(self.__dealloc_def,
                           description='終了関数')
        writer.gen_reprfunc(self.__repr_def,
                            description='repr 関数')
        writer.gen_number(self.__number_gen, self.__number_name)
        writer.gen_sequence(self.__sequence_gen, self.__sequence_name)
        writer.gen_mapping(self.__mapping_gen, self.__mapping_name)
        writer.gen_hashfunc(self.__hash_def,
                            description='hash 関数')
        writer.gen_reprfunc(self.__str_def,
                            description='str 関数')
        writer.gen_richcmpfunc(self.__richcompare_def,
                               description='richcompare 関数')
        writer.gen_methods(self.__method_gen, self.__method_name)
        writer.gen_getset(self.__getset_gen, self.__getset_name)
        writer.gen_initproc(self.__init_def,
                            description='init 関数')
        writer.gen_newfunc(self.__new_def,
                           description='new 関数')
        
    def make_tp_init(self, writer):
        tp_list = []
        tp_list.append(('name', f'"{self.pyname}"'))
        tp_list.append(('basicsize', self.basicsize))
        tp_list.append(('itemsize', self.itemsize))
        if self.__dealloc_def is not None:
            tp_list.append(('dealloc', f'{self.__dealloc_def.name}'))
        if self.__repr_def is not None:
            tp_list.append(('repr', f'{self.__repr_def.name}'))
        if self.__number_name is not None:
            tp_list.append(('as_number', f'{self.__number_name}'))
        if self.__sequence_name is not None:
            tp_list.append(('as_sequence', f'{self.__sequence_name}'))
        if self.__mapping_name is not None:
            tp_list.append(('as_mapping', f'{self.__mapping_name}'))
        if self.__hash_def is not None:
            tp_list.append(('hash', f'{self.__hash_def.name}'))
        if self.__call_def is not None:
            tp_list.append(('call', f'{self.__call_def.name}'))
        if self.__str_def is not None:
            tp_list.append(('str', f'{self.__str_def.name}'))
        tp_list.append(('flags', self.flags))
        tp_list.append(('doc', f'PyDoc_STR("{self.doc_str}")'))
        if self.__richcompare_def is not None:
            tp_list.append(('richcompare', f'{self.__richcompare_def.name}'))
        tp_list.append(('methods', f'{self.__method_name}'))
        tp_list.append(('getset', f'{self.__getset_name}'))
        if self.__init_def is not None:
            tp_list.append(('init', f'{self.__init_def.name}'))
        if self.__new_def is not None:
            tp_list.append(('new', f'{self.__new_def.name}'))
        for name, rval in tp_list:
            writer.gen_assign(f'{self.typename}.tp_{name}', f'{rval}')

    def make_conv(self, writer):
        description = f'{self.classname} を PyObject に変換する．'
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=f'{self.pyclassname}::Conv::operator()',
                                   args=(f'const {self.classname}& val', )):
            writer.gen_auto_assign('type', f'{self.pyclassname}::_typeobject()')
            writer.gen_auto_assign('obj', 'type->tp_alloc(type, 0)')
            writer.gen_auto_assign('obj1', f'reinterpret_cast<{self.objectname}*>(obj)')
            self.__conv_gen(writer)
            writer.gen_return('obj')

    def make_deconv(self, writer):
        description = f'PyObject を {self.classname} に変換する．'
        with writer.gen_func_block(description=description,
                                   return_type='bool',
                                   func_name=f'{self.pyclassname}::Deconv::operator()',
                                   args=('PyObject* obj',
                                         f'{self.classname}& val')):
            self.__deconv_gen(writer)

    def __complete_funcdef(self, funcdef, default_name):
        """FuncDef の名前を補完する．
        """
        if funcdef is None:
            return None
        name = self.__complete(funcdef.name, default_name)
        return FuncDef(name, funcdef.func)
    
    def __complete(self, name, default_name):
        """名前がない場合に名前を補完する．
        """
        if name is None:
            name = default_name
        return self.__check_name(name)

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
