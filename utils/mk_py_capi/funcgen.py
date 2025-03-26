#! /usr/bin/env python3

""" FuncGen の定義ファイル

:file: funcgen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi.codegenbase import CodeGenBase


class PreambleGen(CodeGenBase):
    """共通な定数の定義などを行う．
    """

    def __init__(self, parent):
        super().__init__(parent)
        parent.preamble_gen = self

    def __call__(self):
        pass
