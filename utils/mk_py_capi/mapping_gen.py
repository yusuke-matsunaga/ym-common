#! /usr/bin/env python3

""" MappingGen のクラス定義ファイル

:file: mapping_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple
from .funcgen import LenFuncGen, BinaryFuncGen, ObjObjArgProcGen
from .utils import gen_func, add_member_def


# mapping オブジェクト構造体を表す型
Mapping = namedtuple('Mapping',
                     ['mp_length',
                      'mp_subscript',
                      'mp_ass_subscript'])
        

class MappingGen(Mapping):
    """Mapping オブジェクト構造体を作るクラス
    """

    def __new__(cls, *,
                mp_length=None,
                mp_subscript=None,
                mp_ass_subscript=None):
        if mp_length is not None:
            mp_length = LenFuncGen('mp_length', mp_length)
        if mp_subscript is not None:
            mp_subscript = BinaryFuncGen('mp_subscript', mp_subscript)
        if mp_ass_subscript is not None:
            mp_ass_subscript = ObjObjArgProcGen('mp_ass_subscript', mp_ass_subscript)
        self = super().__new__(cls,
                               mp_length=mp_length,
                               mp_subscript=mp_subscript,
                               mp_ass_subscript=mp_ass_subscript)
        return self
        
    def __call__(self, writer, name):
        # 個々の関数を生成する．
        gen_func(self.mp_length, writer)
        gen_func(self.mp_subscript, writer)
        gen_func(self.mp_ass_subscript, writer)

        # 構造体定義を生成する．
        writer.gen_CRLF()
        writer.gen_comment('Mapping オブジェクト構造体')
        with writer.gen_struct_init_block('PyMappingMethods', name):
            mp_lines = []
            add_member_def(mp_lines, 'mp_length', self.mp_length)
            add_member_def(mp_lines, 'mp_subscript', self.mp_subscript)
            add_member_def(mp_lines, 'mp_ass_subscript', self.mp_ass_subscript)
            writer._write_lines(mp_lines, delim=',')
