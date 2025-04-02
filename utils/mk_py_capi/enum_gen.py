#! /usr/bin/env python3

""" EnumGen のクラス定義ファイル

:file: enum_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple
from .pyobj_gen import PyObjGen


EnumInfo = namedtuple('EnumInfo',
                      ['cval',
                       'pyname',
                       'strname'])

class EnumGen(PyObjGen):

    def __init__(self, *,
                 classname,
                 pyclassname=None,
                 namespace=None,
                 typename=None,
                 objectname=None,
                 pyname,
                 enum_list,
                 header_include_files=[],
                 source_include_files=[]):
        super().__init__(classname=classname,
                         pyclassname=pyclassname,
                         namespace=namespace,
                         typename=typename,
                         objectname=objectname,
                         pyname=pyname,
                         header_include_files=header_include_files,
                         source_include_files=source_include_files)
        self.__enum_list = enum_list
        
        self.add_dealloc(dealloc_func=None)

        def reprfunc(writer):
            with writer.gen_switch_block('val'):
                for enum_info in self.__enum_list:
                    writer.write_line(f'case {enum_info.cval}: repr_str = "{enum_info.strname}"; break;')
        self.add_repr(repr_func=reprfunc)

        def richcmpfunc(writer):
            with writer.gen_if_block(f'{self.pyclassname}::Check(self) && {self.pyclassname}::Check(other)'):
                self.gen_ref_conv(writer, objname='self', refname='val1')
                self.gen_ref_conv(writer, objname='other', refname='val2')
                with writer.gen_if_block('op == Py_EQ'):
                    writer.gen_return_py_bool('val1 == val2')
                with writer.gen_if_block('op == Py_NE'):
                    writer.gen_return_py_bool('val1 != val2')
            writer.write_line('Py_RETURN_NOTIMPLEMENTED')
        self.add_richcompare(cmp_func=richcmpfunc)
