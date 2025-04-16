#! /usr/bin/env python3

""" SequenceGen のクラス定義ファイル

:file: sequence_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple
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

    def __new__(cls, gen, name, *,
                sq_length=None,
                sq_concat=None,
                sq_repeat=None,
                sq_item=None,
                sq_ass_item=None,
                sq_contains=None,
                sq_inplace_concat=None,
                sq_inplace_repeat=None):
        if sq_length is not None:
            sq_length = gen.new_lenfunc('sq_length', sq_length)
        if sq_concat is not None:
            sq_concat = gen.new_binaryfunc('sq_concat', sq_concat)
        if sq_repeat is not None:
            sq_repeat = gen.new_ssizeargfunc('sq_repeat', sq_repeat)
        if sq_item is not None:
            sq_item = gen.new_ssizeargfunc('sq_item', sq_item,
                                           arg2name='index')
        if sq_ass_item is not None:
            sq_ass_item = gen.new_ssizeobjargproc('sq_ass_item', sq_ass_item,
                                                  arg2name='index',
                                                  arg3name='obj')
        if sq_contains is not None:
            sq_contains = gen.new_objobjproc('sq_contains', sq_contains)
        if sq_inplace_concat is not None:
            sq_inplace_concat = gen.new_binaryfunc('sq_inplace_concat', sq_inplace_concat)
        if sq_inplace_repeat is not None:
            sq_inplace_repeat = gen.new_ssizeargfunc('sq_inplace_repeat', sq_inplace_repeat)
        self = super().__new__(cls,
                               sq_length=sq_length,
                               sq_concat=sq_concat,
                               sq_repeat=sq_repeat,
                               sq_item=sq_item,
                               sq_ass_item=sq_ass_item,
                               sq_contains=sq_contains,
                               sq_inplace_concat=sq_inplace_concat,
                               sq_inplace_repeat=sq_inplace_repeat)
        self.typename = gen.typename
        self.name = name
        return self
        
    def __call__(self, writer):
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
        with writer.gen_struct_init_block(structname='PySequenceMethods',
                                          varname=self.name,
                                          comment='Sequence オブジェクト構造体'):
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

    def gen_tp(self, writer):
        writer.gen_assign(f'{self.typename}.tp_as_sequence',
                          f'&{self.name}')
