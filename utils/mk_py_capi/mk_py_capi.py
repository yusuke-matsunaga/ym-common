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
        self.preamble_gen = None
        self.dealloc_gen = None
        self.repr_gen = None
        self.number_gen = None
        self.sequence_gen = None
        self.mapping_gen = None
        self.hash_gen = None
        self.call_gen = None
        self.str_gen = None
        self.richcompare_gen = None
        self.getset_gen = None
        self.init_gen = None
        self.new_gen = None
        self.ex_init_gen = None
        self.conv_gen = None
        self.deconv_gen = None
        self.doc_str = f'{self.classname} object'

        self.__fout = None
        self.__name_dict = set()
        self.__dealloc_name = self.__check_name('dealloc')
        self.__repr_name = self.__check_name('repr')
        self.__number_name = self.__check_name('number')
        self.__sequence_name = self.__check_name('sequence')
        self.__mapping_name = self.__check_name('mapping')
        self.__hash_name = self.__check_name('hash')
        self.__call_name = self.__check_name('call')
        self.__str_name = self.__check_name('str')
        self.__richcompare_name = self.__check_name('richcompare')
        self.__method_name = self.__check_name('method_table')
        self.__getset_name = self.__check_name('getset_table')
        self.__init_name = self.__check_name('init_func')
        self.__new_name = self.__check_name('new_func')
        self.__method_list = []
        self.__indent = 0
        self.__conv_def_pat = re.compile('^(\s)*%%CONV_DEF%%$')
        self.__deconv_def_pat = re.compile('^(\s)*%%DECONV_DEF%%$')
        self.__to_def_pat = re.compile('^(\s)*%%TOPYOBJECT%%$')
        self.__from_def_pat = re.compile('^(\s)*%%FROMPYOBJECT%%$')
        self.__tp_init_pat = re.compile('^(\s)*%%TP_INIT_CODE%%$')
        self.__ex_init_pat = re.compile('^(\s)*%%EX_INIT_CODE%%$')

    def add_method(self, method):
        """メソッド定義を追加する．
        """
        self.__check_name(method.func_name)
        self.__method_list.append(method)

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
        if self.conv_gen is None:
            if self.deconv_gen is None:
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
        if self.deconv_gen is None:
            if self.conv_gen is not None:
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
        if self.conv_gen is not None:
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
        if self.deconv_gen is not None:
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
                if result:
                    # 追加の初期化コードの置換
                    self.indent = len(result.group(1))
                    self.make_ex_init()
                    self.indent = 0
                    continue

                if line == '%%CONV_CODE%%':
                    # Conv 関数の置換
                    self.make_conv()
                    continue

                if line == '%%DECONV_CODE%%':
                    # Deconv 関数の置換
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
        if self.preamble_gen is not None:
            self.preamble_gen()
        
        if self.dealloc_gen is not None:
            self.dealloc_gen(self.__dealloc_name)

        if self.repr_gen is not None:
            self.repr_gen(self.__repr_name)

        if self.number_gen is not None:
            self.number_gen(self.__number_name)

        if self.sequence_gen is not None:
            self.sequence_gen(self.__sequence_name)

        if self.mapping_gen is not None:
            self.mapping_gen(self.__mapping_name)

        if self.hash_gen is not None:
            self.hash_gen(self.__hash_name)

        if self.str_gen is not None:
            self.str_gen(self.__str_name)

        if self.richcompare_gen is not None:
            self.richcompare_gen(self.__richcompare_name)

        if len(self.__method_list) > 0:
            for method in self.__method_list:
                method(method.func_name)

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
                    line += method.func_name
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

        if self.getset_gen is not None:
            self.getset_gen(self.__getset_name)

        if self.init_gen is not None:
            self.init_gen(self.__init_name)

        if self.new_gen is not None:
            self.new_gen(self.__new_name)

    def gen_preamble(self):
        pass
    
    def make_tp_init(self):
        tp_list = []
        tp_list.append(('name', f'"{self.pyname}"'))
        tp_list.append(('basicsize', f'sizeof({self.objectname})'))
        tp_list.append(('itemsize', '0'))
        if self.dealloc_gen is not None:
            tp_list.append(('dealloc', f'{self.__dealloc_name}'))
        if self.repr_gen is not None:
            tp_list.append(('repr', f'{self.__repr_name}'))
        if self.number_gen is not None:
            tp_list.append(('repr', f'{self.__repr_name}'))
        if self.number_gen is not None:
            tp_list.append(('as_number', f'{self.__number_name}'))
        if self.sequence_gen is not None:
            tp_list.append(('as_sequence', f'{self.__sequence_name}'))
        if self.mapping_gen is not None:
            tp_list.append(('as_mapping', f'{self.__mapping_name}'))
        if self.hash_gen is not None:
            tp_list.append(('hash', f'{self.__hash_name}'))
        if self.call_gen is not None:
            tp_list.append(('call', f'{self.__call_name}'))
        if self.str_gen is not None:
            tp_list.append(('str', f'{self.__str_name}'))
        tp_list.append(('flags', 'Py_TPFLAGS_DEFAULT'))
        tp_list.append(('doc', f'PyDoc_STR("{self.doc_str}")'))
        if self.richcompare_gen is not None:
            tp_list.append(('richcompare', f'{self.__richcompare_name}'))
        if len(self.__method_list) > 0:
            tp_list.append(('methods', f'{self.__method_name}'))
        if self.getset_gen is not None:
            tp_list.append(('getset', f'{self.__getset_name}'))
        if self.init_gen is not None:
            tp_list.append(('init', f'{self.__init_name}'))
        if self.new_gen is not None:
            tp_list.append(('new', f'{self.__new_name}'))
        for name, rval in tp_list:
            self.gen_assign(f'{self.typename}.tp_{name}', f'{rval}')
        
    def make_ex_init(self):
        if self.ex_init_gen is not None:
            self.ex_init_gen()

    def make_conv(self):
        if self.conv_gen is not None:
            self.conv_gen()

    def make_deconv(self,):
        if self.deconv_gen is not None:
            self.deconv_gen()

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

    def gen_py_return_none(self):
        """Py_RETURN_NONE を出力する．
        """
        self._write_line('Py_RETURN_NONE')
        
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
    
    def gen_type_error(self, error_msg):
        self.gen_error('PyExc_TypeError', error_msg)

    def gen_value_error(self, error_msg):
        self.gen_error('PyExc_ValueError', error_msg)
        
    def gen_error(self, error_type, error_msg):
        """エラー出力
        """
        self._write_line(f'PyErr_SetString({error_type}, {error_msg});')
        
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
            
