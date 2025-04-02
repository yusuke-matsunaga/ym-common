#! /usr/bin/env python3

""" MethodGen のクラス定義ファイル

:file: method_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple
from .utils import analyze_args


# メソッドを表す型
Method = namedtuple('Method',
                    ['gen',
                     'name',
                     'func_name',
                     'arg_list',
                     'is_static',
                     'has_args',
                     'has_keywords',
                     'func_body',
                     'doc_str'])

class MethodGen:
    """メソッドを作るクラス
    """
    
    def __init__(self, *, module_func=False):
        self.__method_list = []
        self.__module_func = module_func

    def add(self, gen, func_name, *,
            name,
            arg_list,
            is_static,
            func_body,
            doc_str):
        has_args, has_keywords = analyze_args(arg_list)
        if func_body is None:
            def default_body(writer):
                pass
            func_body = default_body
        self.__method_list.append(Method(gen=gen,
                                         name=name,
                                         func_name=func_name,
                                         arg_list=arg_list,
                                         is_static=is_static,
                                         has_args=has_args,
                                         has_keywords=has_keywords,
                                         func_body=func_body,
                                         doc_str=doc_str))
                                         
    def __call__(self, writer, name):
        # 個々のメソッドの実装コードを生成する．
        for method in self.__method_list:
            if self.__module_func or method.is_static:
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
            with writer.gen_func_block(comment=method.doc_str,
                                       return_type='PyObject*',
                                       func_name=method.func_name,
                                       args=args):
                writer.gen_func_preamble(method.arg_list)
                if not (self.__module_func or method.is_static):
                    method.gen.gen_ref_conv(writer, refname='val')
                method.func_body(writer)

        # メソッドテーブルを生成する．
        with writer.gen_array_block(typename='PyMethodDef',
                                    arrayname=name,
                                    comment='メソッド定義'):
            for method in self.__method_list:
                writer.write_line(f'{{"{method.name}",')
                writer.indent_inc(1)
                line = ''
                if method.has_keywords:
                    line = 'reinterpret_cast<PyCFunction>('
                line += method.func_name
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
