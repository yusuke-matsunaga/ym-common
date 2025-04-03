#! /usr/bin/env python3

""" EnumGen のクラス定義ファイル

:file: enum_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple
from .pyobj_gen import PyObjGen
from .arg import ObjArg


EnumInfo = namedtuple('EnumInfo',
                      ['cval',
                       'pyname',
                       'strname'])

class EnumGen(PyObjGen):

    def __init__(self, *,
                 classname,
                 pyclassname=None,
                 namespace=None,
                 typename=None,
                 objectname=None,
                 pyname,
                 enum_list,
                 extra_deconv=None,
                 header_include_files=[],
                 source_include_files=[]):
        super().__init__(classname=classname,
                         pyclassname=pyclassname,
                         namespace=namespace,
                         typename=typename,
                         objectname=objectname,
                         pyname=pyname,
                         header_include_files=header_include_files,
                         source_include_files=source_include_files)

        def preamble_body(writer):
            writer.gen_CRLF()
            writer.gen_comment('定数を表すオブジェクト')
            for enum in enum_list:
                writer.gen_vardecl(typename='PyObject*',
                                   varname=f'Const_{enum.cval}',
                                   initializer='nullptr')
            with writer.gen_func_block(comment='定数の登録を行う関数',
                                       return_type='bool',
                                       func_name='reg_const_obj',
                                       args=['const char* name',
                                             f'{classname} val',
                                             'PyObject*& const_obj']):
                self.gen_alloc_code(writer, varname='obj')
                self.gen_obj_conv(writer, objname='obj', varname='my_obj')
                writer.gen_assign('my_obj->mVal', 'val')
                with writer.gen_if_block('PyDict_SetItemString(type->tp_dict, name, obj) < 0'):
                    writer.gen_return('false')
                writer.gen_assign('const_obj', 'obj')
                writer.gen_return('true')
        self.add_preamble(preamble_body)
        
        self.add_dealloc(dealloc_func=None)

        def reprfunc(writer):
            with writer.gen_switch_block('val'):
                for enum_info in enum_list:
                    writer.write_line(f'case {enum_info.cval}: repr_str = "{enum_info.strname}"; break;')
        self.add_repr(repr_func=reprfunc)

        def richcmpfunc(writer):
            with writer.gen_if_block(f'{self.pyclassname}::Check(self) && {self.pyclassname}::Check(other)'):
                self.gen_ref_conv(writer, objname='self', refname='val1')
                self.gen_ref_conv(writer, objname='other', refname='val2')
                with writer.gen_if_block('op == Py_EQ'):
                    writer.gen_return_py_bool('val1 == val2')
                with writer.gen_if_block('op == Py_NE'):
                    writer.gen_return_py_bool('val1 != val2')
            writer.write_line('Py_RETURN_NOTIMPLEMENTED')
        self.add_richcompare(cmp_func=richcmpfunc)

        def new_body(writer):
            writer.gen_return(f'{self.pyclassname}::ToPyObject(val)')
        self.add_new(func_body=new_body,
                     arg_list=[ObjArg(name='val',
                                      cvartype=f'{self.classname}',
                                      cvarname='val',
                                      cvardefault=None,
                                      pyclassname=f'{self.pyclassname}'),])
        
        def init_body(writer):
            writer.gen_comment('定数オブジェクトの生成・登録')
            for enum in enum_list:
                name = enum.pyname
                val = enum.cval
                const_obj = f'Const_{name}'
                with writer.gen_if_block(f'!reg_const_obj("{name}", {val}, {const_obj})'):
                    writer.write_line('goto error;')
        self.add_ex_init(init_body)

        def conv_body(writer):
            with writer.gen_switch_block('val'):
                for enum in enum_list:
                    writer.write_line(f'case {enum.cval}: return Const_{enum.pyname};')
            writer.gen_value_error('"never happen"')
        self.add_conv(conv_body)

        def deconv_body(writer):
            writer.gen_vardecl(typename='std::string',
                               varname='str_val');
            with writer.gen_if_block('PyString::FromPyObject(obj, str_val)'):
                first = True
                for enum in enum_list:
                    condition = f'str_val == "{enum.strname}"'
                    if first:
                        block = writer.gen_if_block(condition)
                        first = False
                    else:
                        block = writer.gen_elseif_block(condition)
                    with block:
                        writer.gen_assign('val', f'{enum.cval}')
                        writer.gen_return('true')
                writer.gen_return('false')
            with writer.gen_if_block(f'{self.pyclassname}::Check(obj)'):
                self.gen_raw_conv(writer)
            writer.gen_return('false')
        self.add_deconv(deconv_body, extra_func=extra_deconv)
