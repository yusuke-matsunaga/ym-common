#! /usr/bin/env python3

""" PyObjGen の全ての要素のデフォルト実装をテストするプログラム

:file: test_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi import PyObjGen


def dummy_func(writer):
    pass


gen = PyObjGen(classname='Test',
               pyname='test')


gen.add_dealloc()
gen.add_repr()
gen.add_hash()
gen.add_call()
gen.add_str()
gen.add_richcompare()
gen.add_nb_add()
gen.add_nb_subtract()
gen.add_nb_multiply()
gen.add_nb_remainder()
gen.add_nb_divmod(expr='divmod(val1, val2)')
gen.add_nb_power(body=dummy_func)
gen.add_nb_negative(body=dummy_func)
gen.add_nb_positive(body=dummy_func)
gen.add_nb_absolute(body=dummy_func)
gen.add_nb_bool(body=dummy_func)
gen.add_nb_invert(body=dummy_func)
gen.add_nb_lshift()
gen.add_nb_rshift()
gen.add_nb_and()
gen.add_nb_xor()
gen.add_nb_or()
gen.add_nb_int(body=dummy_func)
gen.add_nb_float(body=dummy_func)
gen.add_nb_inplace_add()
gen.add_nb_inplace_subtract()
gen.add_nb_inplace_multiply()
gen.add_nb_inplace_remainder()
gen.add_nb_inplace_power(body=dummy_func)
gen.add_nb_inplace_lshift()
gen.add_nb_inplace_rshift()
gen.add_nb_inplace_and()
gen.add_nb_inplace_xor()
gen.add_nb_inplace_or()
gen.add_nb_floor_divide(expr='floor_div(val1, val2)')
gen.add_nb_true_divide()
gen.add_nb_inplace_floor_divide(stmt='floor_div_int(val1, val2)')
gen.add_nb_inplace_true_divide()
gen.add_nb_index(body=dummy_func)
gen.add_nb_matrix_multiply(expr='matmul(val1, val2)')
gen.add_nb_inplace_matrix_multiply(stmt='matmul_int(val1, val2)')

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
