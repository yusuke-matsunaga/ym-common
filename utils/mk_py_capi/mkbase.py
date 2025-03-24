#! /usr/bin/env python3

""" MkBase のクラス定義ファイル

:file: mkbase.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

import os
import datetime


class MkBase:
    """MkHeader/MkSource に共通な基底クラス
    """

    def __init__(self, *,
                 fout,
                 classname,
                 pyclassname,
                 namespace):

    @staticmethod
    def year():
        """現在の年を表す文字列を返す．
        """
        return str(datetime.datetime.now().year)

    @staticmethod
    def template_file(filename):
        """テンプレートファイル名を返す．
        """
        basedir = os.path.dirname(__file__)
        return os.path.join(basedir, filename)

    def _write_line(self, line):
        spc = '  ' * self.__indent
        self.__fout.write(f'{spc}{line}\n')

    def _indent_inc(self):
        self.__indent += 1

    def _indent_dec(self):
        self.__indent -= 1

    def _indent_set(self, val):
        self.__indent = val
