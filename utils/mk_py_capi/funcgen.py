#! /usr/bin/env python3

""" FuncGen の定義ファイル

:file: funcgen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi.codegenbase import CodeGenBase
from mk_py_capi.codeblock import FuncBlock, ArrayBlock


class ArgInfo:
    """引数の情報を表すクラス

    以下の情報を持つ．
    - name: 名前
    - option: 省略可能の場合 True にする．
    - pchar: PyArg_Parse() で用いる型指定文字
    - ptype: pchar が 'O!' の場合の Python の型オブジェクト
    - cvartype: C++ での型
    - cvarname: C++ に変換した時の変数名
    - cvardefault: 省略された時のデフォルト値
    - convgen(): C++ の変数に変換するコードを生成する関数
    """

    def __init__(self, *,
                 name=None,
                 option,
                 pchar,
                 ptype=None,
                 cvartype,
                 cvarname,
                 cvardefault,
                 convgen=None):
        self.name = name
        self.option = option
        self.pchar = pchar
        self.ptype = ptype
        self.cvartype = cvartype
        self.cvarname = cvarname
        self.cvardefault = cvardefault
        self.convgen = convgen

    
class FuncGen(CodeGenBase):
    """関数を実装するためのC++コードを生成するクラス
    """

    def __init__(self, parent, *,
                 name,
                 return_type,
                 func_name,
                 arg_list,
                 is_static,
                 doc_str):
        super().__init__(parent)
        self.name = name
        self.return_type = return_type
        self.func_name = func_name
        self.arg_list = arg_list
        if len(arg_list) == 0:
            self.has_args = False
            self.has_keywords = False
        else:
            self.has_args = True
            for arg in arg_list:
                if arg.name is not None:
                    self.has_keywords = True
        self.is_static = is_static
        self.doc_str = doc_str
    
    def funcgen(self):
        print('funcgen')
        print(f'arg_list = {self.arg_list}')
        if self.is_static:
            args0 = 'PyObject* Py_UNUSED(self)'
        else:
            args0 = 'PyObject* self'
        if self.has_args:
            arg1 = 'PyObject* args'
        else:
            arg1 = 'PyObject* Py_UNUSED(args)'
        if self.has_keywords:
            arg1 += ','
            arg2 = 'PyObject* kwds'
            args = ( args0, arg1, arg2 )
        else:
            args = ( args0, arg1, )
        with FuncBlock(self.parent,
                       description=self.doc_str,
                       return_type=self.return_type,
                       func_name=self.func_name,
                       args=args):
            if self.has_keywords:
                # キーワードテーブルの定義
                kwds_table = 'kwlist'
                with ArrayBlock(self.parent,
                                typename='static const char*',
                                arrayname=kwds_table):
                    for arg in self.arg_list:
                        if arg.name is None:
                            self._write_line('"",')
                        else:
                            self._write_line(f'"{arg.name}",')
                    self._write_line('nullptr')

            # パーズ結果を格納する変数の宣言
            for arg in self.arg_list:
                if arg.pchar == 'O' or arg.pchar == 'O!':
                    self._write_line(f'PyObject* {arg.cvarname}_obj = nullptr;')
                else:
                    self._write_line(f'{arg.cvartype} {arg.cvarname} = {arg.cvardefault};')

            # PyArg_Parse() 用のフォーマット文字列の生成
            fmt_str = ""
            mode = "init" # init|option|keyword の3つ
            for arg in self.arg_list:
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
            if self.has_args:
                if self.has_keywords:
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
                nargs = len(self.arg_list)
                for i, arg in enumerate(self.arg_list):
                    if arg.pchar == 'O!':
                        line = f'{arg.ptype}, &{arg.cvarname}_obj'
                    elif arg.pchar == 'O':
                        line = f'{arg.cvarname}_obj'
                    else:
                        line = f'{arg.cvarname}'
                    if i < nargs - 1:
                        line += ','
                    else:
                        line += ') ) {'
                    self._write_line(line)
                self._indent_dec(delta)
                self._indent_inc()
                self._write_line('return nullptr;')
                self._indent_dec()
                self._write_line('}')

            # PyObject から C++ の変数へ変換する．
            for arg in self.arg_list:
                if arg.convgen is not None:
                    arg.convgen()
                        
            self.bodygen()

    def bodygen(self):
        pass
                    

    
class MethodGen(FuncGen):
    """メソッドを実装するためのC++コードを生成するクラス
    """

    def __init__(self, parent, *,
                 name,
                 func_name,
                 arg_list,
                 is_static,
                 doc_str):
        super().__init__(parent,
                         name=name,
                         return_type='PyObject*',
                         func_name=func_name,
                         arg_list=arg_list,
                         is_static=is_static,
                         doc_str=doc_str)


class NewGen(FuncGen):
    """new 関数を生成するクラス
    """

    def __init__(self, parent, *,
                 arg_list):
        super().__init__(parent,
                         name=None,
                         return_type='PyObject*',
                         func_name=None,
                         arg_list=arg_list,
                         is_static=False,
                         doc_str=None)
        print('NewGen')
        print(f'arg_list = {arg_list}')
        print(f'self.arg_list = {self.arg_list}')
        
    def __call__(self, func_name):
        self.func_name = func_name
        self.funcgen()
        """
        args = ('PyTypeObject* type',
                'PyObject* args',
                'PyObject* kwds')
        with FuncBlock(self.parent,
                       return_type='PyObject*',
                       func_name=func_name,
                       args = args):
            self.bodygen()
        """
                 
