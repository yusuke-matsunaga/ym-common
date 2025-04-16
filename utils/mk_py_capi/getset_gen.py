#! /usr/bin/env python3

""" GetSetGen のクラス定義ファイル

:file: getset_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple


# getter/setterを表す型
GetSet = namedtuple('GetSet',
                    ['gen',
                     'name',
                     'body',
                     'has_closure'])

# 属性を表す型
Attr = namedtuple('Attr',
                  ['name',
                   'getter_name',
                   'setter_name',
                   'closure',
                   'doc_str'])


class GetSetGen:
    """getter/setter を作るクラス
    """

    def __init__(self, gen, name):
        self.typename = gen.typename
        self.name = name
        self.__getter_list = []
        self.__setter_list = []
        self.__attr_list = []
        
    def add_getter(self, gen, func_name, *,
                   has_closure=False,
                   func_body):
        """getter 定義を追加する．
        """
        if func_body is None:
            def default_body(writer):
                pass
            func_body = default_body
        self.__getter_list.append(GetSet(gen, func_name, func_body, has_closure))

    def add_setter(self, gen, func_name, *,
                   has_closure=False,
                   func_body):
        """setter 定義を追加する．
        """
        if func_body is None:
            def default_body(writer):
                pass
            func_body = default_body
        self.__setter_list.append(GetSet(gen, func_name, func_body, has_closure))

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
            # getter 関数が登録されているかチェックする．
            # 非効率な線形探索を用いている．
            for getter in self.__getter_list:
                if getter.name == getter_name:
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
            # setter 関数が登録されているかチェックする．
            # 非効率な線形探索を用いている．
            for setter in self.__setter_list:
                if setter.name == setter_name:
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
        self.__attr_list.append(Attr(name, getter_name, setter_name,
                                     closure, doc_str))

    def __call__(self, writer):
        # getter 関数の生成
        for getter in self.__getter_list:
            arg0 = 'PyObject* self'
            if getter.has_closure:
                arg1 = 'void* closure'
            else:
                arg1 = 'void* Py_UNUSED(closure)'
            args = [ arg0, arg1 ]
            with writer.gen_func_block(return_type='PyObject*',
                                       func_name=getter.name,
                                       args=args):
                getter.gen.gen_ref_conv(writer, refname='val')
                getter.body(writer)
                
        # setter 関数の生成
        for setter in self.__setter_list:
            arg0 = 'PyObject* self'
            arg1 = 'PyObject* obj'
            if setter.has_closure:
                arg2 = 'void* closure'
            else:
                arg2 = 'void* Py_UNUSED(closure)'
            args = [ arg0, arg1, arg2 ]
            with writer.gen_func_block(return_type='int',
                                       func_name=setter.name,
                                       args=args):
                setter.gen.gen_ref_conv(writer, refname='val')
                setter.body(writer)

        # getset テーブルの生成
        with writer.gen_array_block(typename='PyGetSetDef',
                                    arrayname=self.name,
                                    comment='getter/setter定義'):
            for attr in self.__attr_list:
                line = f'{{"{attr.name}", {attr.getter_name}, '
                line += f'{attr.setter_name}, PyDoc_STR("{attr.doc_str}"), '
                line += f'{attr.closure}}},'
                writer.write_line(line)
            writer.gen_comment('end-marker')
            writer.write_line('{nullptr, nullptr, nullptr, nullptr}')

    def gen_tp(self, writer):
        writer.gen_assign(f'{self.typename}.tp_getset',
                          self.name)
