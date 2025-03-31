#! /usr/bin/env python3

""" NumberGen のクラス定義ファイル

:file: number_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple
from .funcgen import UnaryFuncGen, BinaryFuncGen, TernaryFuncGen
from .utils import gen_func, add_member_def


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

    def __new__(cls, gen, *,
                nb_add=None,
                nb_subtract=None,
                nb_multiply=None,
                nb_remainder=None,
                nb_divmod=None,
                nb_power=None,
                nb_negative=None,
                nb_positive=None,
                nb_absolute=None,
                nb_bool=None,
                nb_invert=None,
                nb_lshift=None,
                nb_rshift=None,
                nb_and=None,
                nb_xor=None,
                nb_or=None,
                nb_int=None,
                nb_float=None,
                nb_inplace_add=None,
                nb_inplace_subtract=None,
                nb_inplace_multiply=None,
                nb_inplace_remainder=None,
                nb_inplace_power=None,
                nb_inplace_lshift=None,
                nb_inplace_rshift=None,
                nb_inplace_and=None,
                nb_inplace_xor=None,
                nb_inplace_or=None,
                nb_floor_divide=None,
                nb_true_divide=None,
                nb_inplace_floor_divide=None,
                nb_inplace_true_divide=None,
                nb_index=None,
                nb_matrix_multiply=None,
                nb_inplace_matrix_multiply=None):
        if nb_add is not None:
            nb_add = BinaryFuncGen(gen, 'nb_add', nb_add)
        if nb_subtract is not None:
            nb_subtract = BinaryFuncGen(gen, 'nb_subtract', nb_sbtract)
        if nb_multiply is not None:
            nb_multiply = BinaryFuncGen(gen, 'nb_multiply', nb_multiply)
        if nb_remainder is not None:
            nb_remainder = BinaryFuncGen(gen, 'nb_remainder', nb_remainder)
        if nb_divmod is not None:
            nb_divmod = BinaryFuncGen(gen, 'nb_divmod', nb_divmod)
        if nb_power is not None:
            nb_power = TernaryFuncGen(gen, 'nb_power', nb_power)
        if nb_negative is not None:
            nb_negative = UnaryFuncGen(gen, 'nb_negative', nb_negative)
        if nb_positive is not None:
            nb_positive = UnaryFuncGen(gen, 'nb_positive', nb_positive)
        if nb_absolute is not None:
            nb_absolute = UnaryFuncGen(gen, 'nb_absolute', nb_absolute)
        if nb_bool is not None:
            nb_bool = InquiryGen(gen, 'nb_bool', nb_bool)
        if nb_invert is not None:
            nb_invert = UnaryFuncGen(gen, 'nb_invert', nb_invert)
        if nb_lshift is not None:
            nb_lshift = BinaryFuncGen(gen, 'nb_lshift', nb_lshft)
        if nb_rshift is not None:
            nb_rshift = BinaryFuncGen(gen, 'nb_rshift', nb_rshift)
        if nb_and is not None:
            nb_and = BinaryFuncGen(gen, 'nb_and', nb_and)
        if nb_xor is not None:
            nb_xor = BinaryFuncGen(gen, 'nb_xor', nb_xor)
        if nb_or is not None:
            nb_or = BinaryFuncGen(gen, 'nb_or', nb_or)
        if nb_int is not None:
            nb_int = UnaryFuncGen(gen, 'nb_int', nb_int)
        if nb_float is not None:
            nb_float = UnaryFuncGen(gen, 'nb_float', nb_float)
        if nb_inplace_add is not None:
            nb_inplace_add = BinaryFuncGen(gen, 'nb_inplace_add',
                                           nb_inplace_add)
        if nb_inplace_subtract is not None:
            nb_inplace_subtract = BinaryFuncGen(gen, 'nb_inplace_subtract',
                                                nb_inplace_sbtract)
        if nb_inplace_multiply is not None:
            nb_inplace_multiply = BinaryFuncGen(gen, 'nb_inplace_multiply',
                                                nb_inplace_multiply)
        if nb_inplace_remainder is not None:
            nb_inplace_remainder = BinaryFuncGen(gen, 'nb_inplace_remainder',
                                                 nb_inplace_remainder)
        if nb_inplace_power is not None:
            nb_inplace_power = TernaryFuncGen(gen, 'nb_inplace_power',
                                              nb_inplace_power)
        if nb_inplace_lshift is not None:
            nb_inplace_lshift = BinaryFuncGen(gen, 'nb_inplace_lshift',
                                              nb_inplace_lshft)
        if nb_inplace_rshift is not None:
            nb_inplace_rshift = BinaryFuncGen(gen, 'nb_inplace_rshift',
                                              nb_inplace_rshift)
        if nb_inplace_and is not None:
            nb_inplace_and = BinaryFuncGen(gen, 'nb_inplace_and',
                                           nb_inplace_and)
        if nb_inplace_xor is not None:
            nb_inplace_xor = BinaryFuncGen(gen, 'nb_inplace_xor',
                                           nb_inplace_xor)
        if nb_inplace_or is not None:
            nb_inplace_or = BinaryFuncGen(gen, 'nb_inplace_or',
                                          nb_inplace_or)
        if nb_floor_divide is not None:
            nb_floor_divide = BinaryFuncGen(gen, 'nb_floor_divide',
                                            nb_floor_divide)
        if nb_true_divide is not None:
            nb_true_divide = BinaryFuncGen(gen, 'nb_true_divide',
                                           nb_true_divide)
        if nb_inplace_floor_divide is not None:
            nb_inplace_floor_divide = BinaryFuncGen(gen, 'nb_inplace_floor_divide',
                                                    nb_inplace_floor_divide)
        if nb_inplace_true_divide is not None:
            nb_inplace_true_divide = BinaryFuncGen(gen, 'nb_inplace_true_divide',
                                                   nb_inplace_true_divide)
        if nb_index is not None:
            nb_index = UnaryFuncGen(gen, 'nb_index', nb_index)
        if nb_matrix_multiply is not None:
            nb_matrix_multiply = BinaryFuncGen(gen, 'nb_matrix_multiply',
                                               nb_matrix_multiply)
        if nb_inplace_matrix_multiply is not None:
            nb_inplace_matrix_multiply = BinaryFuncGen(gen, 'nb_inplace_matrix_multiply',
                                                       nb_inplace_matrix_multiply)
        self = super().__new__(cls,
                               nb_add=nb_add,
                               nb_subtract=nb_subtract,
                               nb_multiply=nb_multiply,
                               nb_remainder=nb_remainder,
                               nb_divmod=nb_divmod,
                               nb_power=nb_power,
                               nb_lshift=nb_lshift,
                               nb_rshift=nb_rshift,
                               nb_and=nb_and,
                               nb_xor=nb_xor,
                               nb_or=nb_or,
                               nb_int=nb_int,
                               nb_float=nb_float,
                               nb_inplace_add=nb_inplace_add,
                               nb_inplace_subtract=nb_inplace_subtract,
                               nb_inplace_multiply=nb_inplace_multiply,
                               nb_inplace_remainder=nb_inplace_remainder,
                               nb_inplace_power=nb_inplace_power,
                               nb_inplace_lshift=nb_inplace_lshift,
                               nb_inplace_rshift=nb_inplace_rshift,
                               nb_inplace_and=nb_inplace_and,
                               nb_inplace_xor=nb_inplace_xor,
                               nb_inplace_or=nb_inplace_or,
                               nb_floor_divide=nb_floor_divide,
                               nb_true_divide=nb_true_divide,
                               nb_index=nb_index,
                               nb_matrix_multiply=nb_matrix_multiply,
                               nb_inplace_matrix_multiply=nb_inplace_matrix_multiply)
        return self

    def __call__(self, writer, name):
        # 個々の関数を生成する．
        gen_func(self.nb_add, writer)
        gen_func(self.nb_subtract, writer)
        gen_func(self.nb_multiply, writer)
        gen_func(self.nb_remainder, writer)
        gen_func(self.nb_divmod, writer)
        gen_func(self.nb_power, writer)
        gen_func(self.nb_negative, writer)
        gen_func(self.nb_positive, writer)
        gen_func(self.nb_absolute, writer)
        gen_func(self.nb_bool, writer)
        gen_func(self.nb_invert, writer)
        gen_func(self.nb_lshift, writer)
        gen_func(self.nb_rshift, writer)
        gen_func(self.nb_and, writer)
        gen_func(self.nb_xor, writer)
        gen_func(self.nb_or, writer)
        gen_func(self.nb_int, writer)
        gen_func(self.nb_float, writer)
        gen_func(self.nb_inplace_add, writer)
        gen_func(self.nb_inplace_subtract, writer)
        gen_func(self.nb_inplace_multiply, writer)
        gen_func(self.nb_inplace_remainder, writer)
        gen_func(self.nb_inplace_power, writer)
        gen_func(self.nb_inplace_lshift, writer)
        gen_func(self.nb_inplace_rshift, writer)
        gen_func(self.nb_inplace_and, writer)
        gen_func(self.nb_inplace_xor, writer)
        gen_func(self.nb_inplace_or, writer)
        gen_func(self.nb_floor_divide, writer)
        gen_func(self.nb_true_divide, writer)
        gen_func(self.nb_inplace_floor_divide, writer)
        gen_func(self.nb_inplace_true_divide, writer)
        gen_func(self.nb_index, writer)
        gen_func(self.nb_matrix_multiply,writer)
        gen_func(self.nb_inplace_matrix_multiply, writer)

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
