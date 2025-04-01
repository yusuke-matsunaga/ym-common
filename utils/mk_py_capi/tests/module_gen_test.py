#! /usr/bin/env python3

""" ModuleGen の全ての要素のデフォルト実装をテストするプログラム

:file: module_gen_test.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi import ModuleGen

gen = ModuleGen(modulename='test',
                submodule_list=[('ymbase', 'PyInit_ymbase')],
                pyclass_list=['PyJsonValue'])

gen.make_source()
                
