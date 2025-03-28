#! /usr/bin/env python3

""" MethodGen のクラス定義ファイル

:file: method_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple


# メソッドを表す型
Method = namedtuple('Method',
                    ['name',
                     'func_def',
                     'is_static',
                     'has_args',
                     'has_keywords',
                     'doc_str'])

class MethodGen:
    """メソッドを作るクラス
    """
    
    def __init__(self):
        self.__method_list = []

    def add(self, *,
            name,
            func_def,
            is_static,
            has_args,
            has_keywords,
            doc_str):
        self.__method_list.append(Method(name=name,
                                         func_def=func_def,
                                         is_static=is_static,
                                         has_args=has_args,
                                         has_keywords=has_keywords,
                                         doc_str=doc_str))
                                         
    def __call__(self, writer, name):
        # 個々のメソッドの実装コードを生成する．
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
            func_def = method.func_def
            with writer.gen_func_block(description=method.doc_str,
                                       return_type='PyObject*',
                                       func_name=func_def.name,
                                       args=args):
                writer.gen_func_preamble(func_def.arg_list)
                func_def.func(writer)

        # メソッドテーブルを生成する．
        writer.gen_CRLF()
        writer.gen_comment('メソッド定義')
        with writer.gen_array_block(typename='PyMethodDef',
                                    arrayname=name):
            for method in self.__method_list:
                writer.write_line(f'{{"{method.name}",')
                writer.indent_inc(1)
                line = ''
                if method.has_keywords:
                    line = 'reinterpret_cast<PyCFunction>('
                line += method.func_def.name
                if method.has_keywords:
                    line += ')'
                line += ','
                writer.write_line(line)
                if method.has_args:
                    line = 'METH_VARARGS'
                    if method.has_keywords:
                        line += ' | METH_KEYWORDS'
                else:
                    line = 'METH_NOARGS'
                if method.is_static:
                    line += ' | METH_STATIC'
                line += ','
                writer.write_line(line)
                line = f'PyDoc_STR("{method.doc_str}")}},'
                writer.write_line(line)
                writer.indent_dec(1)
            writer.gen_comment('end-marker')
            writer.write_line('{nullptr, nullptr, 0, nullptr}')
