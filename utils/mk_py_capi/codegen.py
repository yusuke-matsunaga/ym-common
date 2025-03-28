#! /usr/bin/env python3

""" CodeGen のクラス定義ファイル

:file: codegen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple


# 基本情報
CoreInfo = namedtuple('CoreInfo',
                      ['classname',
                       'pyclassname',
                       'namespace',
                       'typename',
                       'objectname',
                       'pyname'])


class CodeGen(CoreInfo):

    def __new__(cls, *,
                classname,
                pyclassname=None,
                namespace=None,
                typename=None,
                objectname=None,
                pyname):
        if pyclassname is None:
            pyclassname = f'Py{classname}'
        if typename is None:
            typename = f'{classname}_Type'
        if objectname is None:
            objectname = f'{classname}_Object'
        return super().__new__(cls,
                               classname,
                               pyclassname,
                               namespace,
                               typename,
                               objectname,
                               pyname)

    def core_info(self):
        return CoreInfo(classname=self.classname,
                        pyclassname=self.pyclassname,
                        namespace=self.namespace,
                        typename=self.typename,
                        objectname=self.objectname,
                        pyname=self.pyname)
