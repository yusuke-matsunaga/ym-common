#! /usr/bin/env python3

""" SequenceGen のクラス定義ファイル

:file: sequence_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple
from .utils import add_member_def


# sequence オブジェクト構造体を表す型
Sequence = namedtuple('Sequence',
                      ['sq_length',
                       'sq_concat',
                       'sq_repeat',
                       'sq_item',
                       'sq_ass_item',
                       'sq_contains',
                       'sq_inplace_concat',
                       'sq_inplace_repeat'])


class SequenceGen(Sequence):
    """Sequence オブジェクト構造体を作るクラス
    """

    def __call__(self, writer, name):
        # 個々の関数を生成する．
        writer.gen_lenfunc(self.sq_length)
        writer.gen_binaryfunc(self.sq_concat)
        writer.gen_ssizeargfunc(self.sq_repeat)
        writer.gen_ssizeargfunc(self.sq_item)
        writer.gen_ssizeobjargproc(self.sq_ass_item)
        writer.gen_objobjproc(self.sq_contains)
        writer.gen_binaryfunc(self.sq_inplace_concat)
        writer.gen_ssizeargfunc(self.sq_inplace_repeat)

        # 構造体定義を生成する．
        writer.gen_CRLF()
        writer.gen_comment('Sequence オブジェクト構造体')
        with writer.gen_struct_init_block('PySequenceMethods', name):
            sq_lines = []
            add_member_def(sq_lines, 'sq_length', self.sq_length)
            add_member_def(sq_lines, 'sq_concat', self.sq_concat)
            add_member_def(sq_lines, 'sq_repeat', self.sq_repeat)
            add_member_def(sq_lines, 'sq_item', self.sq_item)
            add_member_def(sq_lines, 'sq_ass_item', self.sq_ass_item)
            add_member_def(sq_lines, 'sq_contains', self.sq_contains)
            add_member_def(sq_lines, 'sq_inplace_concat', self.sq_inplace_concat)
            add_member_def(sq_lines, '.sq_inplace_repeat', self.sq_inplace_repeat)
            writer.write_lines(sq_lines, delim=',')
