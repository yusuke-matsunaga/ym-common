#! /usr/bin/env python3

""" GenBase のクラス定義ファイル

:file: genbase.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

import os
import datetime


class GenBase:
    """PyObject の CAPI 出力用の基底クラス
    """

    def __init__(self):
        # 出力するC++の変数名の重複チェック用の辞書
        self.__name_dict = set()

    def make_file(self, *,
                  template_file,
                  writer,
                  gen_list = [],
                  replace_list = []):
        with open(template_file, 'rt') as fin:
            for line in fin:
                # 余分な改行を削除
                line = line.rstrip()

                for gen in gen_list:
                    # 特定のパタンに対する処理を行う．
                    if gen(line, writer):
                        break
                else:
                    # すべてにマッチしなかったので置換を行って出力する．
                    for rep_pat, rep_val in replace_list:
                        # 置換パタンによる置き換え
                        line = line.replace(rep_pat, rep_val)
                    writer.write_line(line)

    def complete_name(self, name, default_name):
        """名前がない場合に名前を補完する．
        """
        if name is None:
            name = default_name
        return self.check_name(name)

    def check_name(self, name):
        """名前が重複していないかチェックする．

        重複していたら例外を送出する．
        """
        if name in self.__name_dict:
            raise ValueError(f'{name} is already in use')
        self.__name_dict.add(name)
        return name

    @staticmethod
    def year():
        """現在の年を表す文字列を返す．
        """
        return str(datetime.datetime.now().year)

    @staticmethod
    def template_file(filename):
        """テンプレートファイル名を返す．
        """
        # テンプレートファイルは 'templates' の下にあると仮定している．
        basedir = os.path.dirname(__file__)
        return os.path.join(basedir, 'templates', filename)


class IncludesGen:
    """%%INCLUDES%% の置換を行うクラス
    """
    def __init__(self, include_files):
        self.__include_files = include_files

    def __call__(self, line, writer):
        if line == '%%INCLUDES%%':
            # インクルードファイルの置換
            for filename in self.__include_files:
                writer.gen_include(filename)
            return True
        return False


class BeginNamespaceGen:
    """%%BEGIN_NAMESPACE%% の置換を行うクラス
    """
    def __init__(self, namespace):
        self.__namespace = namespace

    def __call__(self, line, writer):
        if line == '%%BEGIN_NAMESPACE%%':
            if self.__namespace is not None:
                # 名前空間の開始
                writer.write_line(f'BEGIN_NAMESPACE_{self.__namespace}')
            return True
        return False


class EndNamespaceGen:
    """%%END_NAMESPACE%% の置換を行うクラス
    """
    def __init__(self, namespace):
        self.__namespace = namespace

    def __call__(self, line, writer):
        if line == '%%END_NAMESPACE%%':
            if self.__namespace is not None:
                # 名前空間の終了
                writer.write_line(f'END_NAMESPACE_{self.__namespace}')
            return True
        return False
