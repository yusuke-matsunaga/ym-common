#! /usr/bin/env python3

""" MethodGen のクラス定義ファイル

:file: method_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple
from .funcgen import CArg
from .utils import analyze_args


# メソッドを表す型
Method = namedtuple('Method',
                    ['gen',
                     'name',
                     'func_name',
                     'arg_parser',
                     'is_static',
                     'func_body',
                     'doc_str'])

class NullParser:
    """引数を取らない場合のダミーパーサー
    """

    def __init__(self):
        pass

    def has_args(self):
        return False

    def has_keywords(self):
        return False

    def __call__(self, writer):
        pass


class DefaultParser:
    """通常の引数パーサー
    """

    def __init__(self, arg_list):
        self.__arg_list = arg_list
        has_args, has_keywords = analyze_args(arg_list)
        self.__has_args = has_args
        self.__has_keywords = has_keywords

    def has_args(self):
        return self.__has_args

    def has_keywords(self):
        return self.__has_keywords

    def __call__(self, writer):
        writer.gen_arg_parser(self.__arg_list)


class MethodGen:
    """メソッドを作るクラス
    """

    def __init__(self, gen, name, *, module_func=False):
        self.__gen = gen
        self.name = name
        self.__method_list = []
        self.__module_func = module_func

    def add(self, func_name, *,
            name,
            arg_list,
            arg_parser,
            is_static,
            func_body,
            doc_str):
        if arg_list is None:
            if arg_parser is None:
                arg_parser = NullParser()
        else:
            assert arg_parser is None
            arg_parser = DefaultParser(arg_list)
        if func_body is None:
            def default_body(writer):
                pass
            func_body = default_body
        self.__method_list.append(Method(gen=self.__gen,
                                         name=name,
                                         func_name=func_name,
                                         arg_parser=arg_parser,
                                         is_static=is_static,
                                         func_body=func_body,
                                         doc_str=doc_str))

    def __call__(self, writer):
        # 個々のメソッドの実装コードを生成する．
        for method in self.__method_list:
            if self.__module_func or method.is_static:
                self_unused = True
            else:
                self_unused = False
            arg0 = CArg.Self(unused=self_unused)
            args_unused = not method.arg_parser.has_args()
            arg1 = CArg.Args(unused=args_unused)
            args = [arg0, arg1]
            if method.arg_parser.has_keywords():
                args += [CArg.Kwds()]
            with writer.gen_func_block(comment=method.doc_str,
                                       return_type='PyObject*',
                                       func_name=method.func_name,
                                       args=args):
                method.arg_parser(writer)
                if not (self.__module_func or method.is_static):
                    self.__gen.gen_ref_conv(writer, refname='val')
                method.func_body(writer)

        # メソッドテーブルを生成する．
        with writer.gen_array_block(typename='PyMethodDef',
                                    arrayname=self.name,
                                    comment='メソッド定義'):
            for method in self.__method_list:
                writer.write_line(f'{{"{method.name}",')
                writer.indent_inc(1)
                line = ''
                if method.arg_parser.has_keywords():
                    line = 'reinterpret_cast<PyCFunction>('
                line += method.func_name
                if method.arg_parser.has_keywords():
                    line += ')'
                line += ','
                writer.write_line(line)
                if method.arg_parser.has_args():
                    line = 'METH_VARARGS'
                    if method.arg_parser.has_keywords():
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

    def gen_tp(self, writer):
        writer.gen_assign(f'{self.__gen.typename}.tp_methods',
                          self.name)
