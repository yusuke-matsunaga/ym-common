#! /usr/bin/env python3

""" PyObjGen の全ての要素のデフォルト実装をテストするプログラム

:file: test_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi import PyObjGen

gen = PyObjGen(classname='Test',
               pyname='test')

def dummy_func(writer):
    pass

gen.add_dealloc()
gen.add_repr()
gen.add_hash()
gen.add_call()
gen.add_str()
gen.add_richcompare()
gen.add_number(
    nb_add=dummy_func,
    nb_subtract=dummy_func,
    nb_multiply=dummy_func,
    nb_remainder=dummy_func,
    nb_divmod=dummy_func,
    nb_power=dummy_func,
    nb_negative=dummy_func,
    nb_positive=dummy_func,
    nb_absolute=dummy_func,
    nb_bool=dummy_func,
    nb_invert=dummy_func,
    nb_lshift=dummy_func,
    nb_rshift=dummy_func,
    nb_and=dummy_func,
    nb_xor=dummy_func,
    nb_or=dummy_func,
    nb_int=dummy_func,
    nb_float=dummy_func,
    nb_inplace_add=dummy_func,
    nb_inplace_subtract=dummy_func,
    nb_inplace_multiply=dummy_func,
    nb_inplace_remainder=dummy_func,
    nb_inplace_power=dummy_func,
    nb_inplace_lshift=dummy_func,
    nb_inplace_rshift=dummy_func,
    nb_inplace_and=dummy_func,
    nb_inplace_xor=dummy_func,
    nb_inplace_or=dummy_func,
    nb_floor_divide=dummy_func,
    nb_true_divide=dummy_func,
    nb_inplace_floor_divide=dummy_func,
    nb_inplace_true_divide=dummy_func,
    nb_index=dummy_func,
    nb_matrix_multiply=dummy_func,
    nb_inplace_matrix_multiply=dummy_func
)
gen.add_sequence(
    sq_length=dummy_func,
    sq_concat=dummy_func,
    sq_repeat=dummy_func,
    sq_item=dummy_func,
    sq_ass_item=dummy_func,
    sq_contains=dummy_func,
    sq_inplace_concat=dummy_func,
    sq_inplace_repeat=dummy_func
)
gen.add_mapping(
    mp_length=dummy_func,
    mp_subscript=dummy_func,
    mp_ass_subscript=dummy_func
)
gen.add_init()
gen.add_new()
gen.add_method('test_method')
gen.add_getter('get1')
gen.add_setter('set1')
gen.add_attr('attr1',
             getter_name='get1',
             setter_name='set1')
gen.add_conv('default')
gen.add_deconv('default', error_value='Test::error()')

gen.make_header()

gen.make_source()
