#! /usr/bin/env python3

""" SequenceGen のクラス定義ファイル

:file: sequence_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple
from .funcgen import LenFuncGen, BinaryFuncGen
from .funcgen import SsizeArgFuncGen, SsizeObjArgProcGen, ObjObjProcGen
from .utils import gen_func, add_member_def



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

    def __new__(cls, *,
                sq_length=None,
                sq_concat=None,
                sq_repeat=None,
                sq_item=None,
                sq_ass_item=None,
                sq_contains=None,
                sq_inplace_concat=None,
                sq_inplace_repeat=None):
        if sq_length is not None:
            sq_length = LenFuncGen('sq_length', sq_length)
        if sq_concat is not None:
            sq_concat = BinaryFuncGen('sq_concat', sq_concat)
        if sq_repeat is not None:
            sq_repeat = SsizeArgFuncGen('sq_repeat', sq_repeat)
        if sq_item is not None:
            sq_item = SsizeArgFuncGen('sq_item', sq_item)
        if sq_ass_item is not None:
            sq_ass_item = SsizeObjArgProcGen('sq_ass_item', sq_ass_item)
        if sq_contains is not None:
            sq_contains = ObjObjProcGen('sq_contains', sq_contains)
        if sq_inplace_concat is not None:
            sq_inplace_concat = BinaryFuncGen('sq_inplace_concat', sq_inplace_concat)
        if sq_inplace_repeat is not None:
            sq_inplace_repeat = SsizeArgFuncGen('sq_inplace_repeat', sq_inplace_repeat)
        self = super().__new__(cls,
                               sq_length=sq_length,
                               sq_concat=sq_concat,
                               sq_repeat=sq_repeat,
                               sq_item=sq_item,
                               sq_ass_item=sq_ass_item,
                               sq_contains=sq_contains,
                               sq_inplace_concat=sq_inplace_concat,
                               sq_inplace_repeat=sq_inplace_repeat)
        return self
        
    def __call__(self, writer, name):
        # 個々の関数を生成する．
        gen_func(self.sq_length, writer)
        gen_func(self.sq_concat, writer)
        gen_func(self.sq_repeat, writer)
        gen_func(self.sq_item, writer)
        gen_func(self.sq_ass_item, writer)
        gen_func(self.sq_contains, writer)
        gen_func(self.sq_inplace_concat, writer)
        gen_func(self.sq_inplace_repeat, writer)

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
