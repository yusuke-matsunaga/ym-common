#! /usr/bin/env python3

""" NumberGen のクラス定義ファイル

:file: number_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple
from .utils import add_member_def


# number オブジェクト構造体を表す型
Number = namedtuple('Number',
                    ['nb_add',
                     'nb_subtract',
                     'nb_multiply',
                     'nb_remainder',
                     'nb_divmod',
                     'nb_power',
                     'nb_negative',
                     'nb_positive',
                     'nb_absolute',
                     'nb_bool',
                     'nb_invert',
                     'nb_lshift',
                     'nb_rshift',
                     'nb_and',
                     'nb_xor',
                     'nb_or',
                     'nb_int',
                     'nb_float',
                     'nb_inplace_add',
                     'nb_inplace_subtract',
                     'nb_inplace_multiply',
                     'nb_inplace_remainder',
                     'nb_inplace_power',
                     'nb_inplace_lshift',
                     'nb_inplace_rshift',
                     'nb_inplace_and',
                     'nb_inplace_xor',
                     'nb_inplace_or',
                     'nb_floor_divide',
                     'nb_true_divide',
                     'nb_inplace_floor_divide',
                     'nb_inplace_true_divide',
                     'nb_index',
                     'nb_matrix_multiply',
                     'nb_inplace_matrix_multiply'])

        
class NumberGen(Number):
    """Number オブジェクト構造体を作るクラス
    """
    
    def __call__(self, writer, name):
        # 個々の関数を生成する．
        writer.gen_binaryfunc(self.nb_add)
        writer.gen_binaryfunc(self.nb_subtract)
        writer.gen_binaryfunc(self.nb_multiply)
        writer.gen_binaryfunc(self.nb_remainder)
        writer.gen_binaryfunc(self.nb_divmod)
        writer.gen_ternaryfunc(self.nb_power)
        writer.gen_unaryfunc(self.nb_negative)
        writer.gen_unaryfunc(self.nb_positive)
        writer.gen_unaryfunc(self.nb_absolute)
        writer.gen_inquiry(self.nb_bool)
        writer.gen_unaryfunc(self.nb_invert)
        writer.gen_binaryfunc(self.nb_lshift)
        writer.gen_binaryfunc(self.nb_rshift)
        writer.gen_binaryfunc(self.nb_and)
        writer.gen_binaryfunc(self.nb_xor)
        writer.gen_binaryfunc(self.nb_or)
        writer.gen_unaryfunc(self.nb_int)
        writer.gen_unaryfunc(self.nb_float)
        writer.gen_binaryfunc(self.nb_inplace_add)
        writer.gen_binaryfunc(self.nb_inplace_subtract)
        writer.gen_binaryfunc(self.nb_inplace_multiply)
        writer.gen_binaryfunc(self.nb_inplace_remainder)
        writer.gen_ternaryfunc(self.nb_inplace_power)
        writer.gen_binaryfunc(self.nb_inplace_lshift)
        writer.gen_binaryfunc(self.nb_inplace_rshift)
        writer.gen_binaryfunc(self.nb_inplace_and)
        writer.gen_binaryfunc(self.nb_inplace_xor)
        writer.gen_binaryfunc(self.nb_inplace_or)
        writer.gen_binaryfunc(self.nb_floor_divide)
        writer.gen_binaryfunc(self.nb_true_divide)
        writer.gen_binaryfunc(self.nb_inplace_floor_divide)
        writer.gen_binaryfunc(self.nb_inplace_true_divide)
        writer.gen_unaryfunc(self.nb_index)
        writer.gen_binaryfunc(self.nb_matrix_multiply)
        writer.gen_binaryfunc(self.nb_inplace_matrix_multiply)

        # 構造体定義を生成する．
        writer.gen_CRLF()
        writer.gen_comment('Numberオブジェクト構造体')
        with writer.gen_struct_init_block('PyNumberMethods', name):
            nb_lines = []
            add_member_def(nb_lines, 'nb_add', self.nb_add)
            add_member_def(nb_lines, 'nb_subtract', self.nb_subtract)
            add_member_def(nb_lines, 'nb_multiply', self.nb_multiply)
            add_member_def(nb_lines, 'nb_remainder', self.nb_remainder)
            add_member_def(nb_lines, 'nb_divmod', self.nb_divmod)
            add_member_def(nb_lines, 'nb_power', self.nb_power)
            add_member_def(nb_lines, 'nb_negative', self.nb_negative)
            add_member_def(nb_lines, 'nb_positive', self.nb_positive)
            add_member_def(nb_lines, 'nb_absolute', self.nb_absolute)
            add_member_def(nb_lines, 'nb_bool', self.nb_bool)
            add_member_def(nb_lines, 'nb_invert', self.nb_invert)
            add_member_def(nb_lines, 'nb_lshift', self.nb_lshift)
            add_member_def(nb_lines, 'nb_rshift', self.nb_rshift)
            add_member_def(nb_lines, 'nb_and', self.nb_and)
            add_member_def(nb_lines, 'nb_xor', self.nb_xor)
            add_member_def(nb_lines, 'nb_or', self.nb_or)
            add_member_def(nb_lines, 'nb_int', self.nb_int)
            add_member_def(nb_lines, 'nb_float', self.nb_float)
            add_member_def(nb_lines, 'nb_inplace_add', self.nb_inplace_add)
            add_member_def(nb_lines, 'nb_inplace_subtract', self.nb_inplace_subtract)
            add_member_def(nb_lines, 'nb_inplace_multiply', self.nb_inplace_multiply)
            add_member_def(nb_lines, 'nb_inplace_remainder', self.nb_inplace_remainder)
            add_member_def(nb_lines, 'nb_inplace_power', self.nb_inplace_power)
            add_member_def(nb_lines, 'nb_inplace_invert', self.nb_inplace_invert)
            add_member_def(nb_lines, 'nb_inplace_lshift', self.nb_inplace_lshift)
            add_member_def(nb_lines, 'nb_inplace_rshift', self.nb_inplace_rshift)
            add_member_def(nb_lines, 'nb_inplace_and', self.nb_inplace_and)
            add_member_def(nb_lines, 'nb_inplace_xor', self.nb_inplace_xor)
            add_member_def(nb_lines, 'nb_inplace_or', self.nb_inplace_or)
            add_member_def(nb_lines, 'nb_floor_divide', self.nb_floor_divide)
            add_member_def(nb_lines, 'nb_true_divide', self.nb_true_divide)
            add_member_def(nb_lines, 'nb_inplace_floor_divide',
                           self.nb_inplace_floor_divide)
            add_member_def(nb_lines, 'nb_inplace_true_divide',
                           self.nb_inplace_true_divide)
            add_member_def(nb_lines, 'nb_index', self.nb_index)
            add_member_def(nb_lines, 'nb_matrix_multiply', self.nb_matrix_multiply)
            add_member_def(nb_lines, 'nb_inplace_matrix_multiply',
                           self.nb_inplace_matrix_multiply)
            writer._write_lines(nb_lines, delim=',')
