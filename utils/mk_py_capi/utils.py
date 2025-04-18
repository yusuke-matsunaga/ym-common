#! /usr/bin/env python3

""" いくつかの便利関数を集めたもの

:file: utils.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""


def analyze_args(arg_list):
    """引数のリストから特徴を解析する．

    has_args, has_keywords のタプルを返す．
    """
    has_args = False
    has_keywords = False
    if len(arg_list) > 0:
        has_args = True
        for arg in arg_list:
            if arg.name is not None:
                has_keywords = True
    return has_args, has_keywords


def gen_func(func_gen, writer, *,
             comment=None,
             comments=None):
    if func_gen is not None:
        func_gen(writer,
                 comment=comment,
                 comments=comments)


def add_member_def(line_list, member_name, func_def):
    """メンバ関数定義用の記述を作る．
    """
    if func_def is not None:
        line = f'.{member_name} = {func_def.name}'
        line_list.append(line)
