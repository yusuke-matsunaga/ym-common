#! /usr/bin/env python3

""" ModuleGen のクラス定義ファイル

:file: module_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

import re
import sys
from .genbase import GenBase


class ModuleGen(GenBase):
    """Python モジュールの初期化コードを生成するクラス
    """

    def __init__(self, *,
                 modulename,
                 namespace=None,
                 doc_str=None):
        super().__init__()
        self.modulename = modulename
        self.namespace = namespace
        self.doc_str = doc_str

    def make_source(self, fout=sys.stdout):
        """初期化コードを出力する．
        """
        
        # テンプレートファイルは同じディレクトリにあると仮定している．
        template_file = self.template_file('custom_module.cc')

        # 結果のファイル名
        source_file = f'{self.modulename}_module.cc'

        writer = CxxWriter(fout=fout)
        with open(template_file, 'rt') as fin:
            for line in fin:
                # 余分な改行を削除
                line = line.rstrip()

                if line == '%%INCLUDES%%':
