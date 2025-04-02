#! /usr/bin/env python3

""" EnumGen のテストプログラム

:file: enum_gen_test.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi import EnumGen, EnumInfo


gen = EnumGen(classname='Color',
              pyname='Color',
              enum_list=[EnumInfo('RED', 'Red', 'red'),
                         EnumInfo('BLUE', 'Blue', 'blue'),
                         EnumInfo('GREEN', 'Green', 'green')])

gen.make_header()
gen.make_source()
