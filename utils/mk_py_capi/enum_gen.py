#! /usr/bin/env python3

""" EnumGen のクラス定義ファイル

:file: enum_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from collections import namedtuple
from .pyobj_gen import PyObjGen
from .arg import ObjConvArg


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
                 none_value=None,
                 ignore_case=False,
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
                                   varname=f'Const_{enum.pyname}',
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
                writer.write_line('Py_INCREF(obj);')
                writer.gen_assign('const_obj', 'obj')
                writer.gen_return('true')
        self.add_preamble(preamble_body)
        
        self.add_dealloc(func_body=None)

        def reprfunc(writer):
            writer.gen_vardecl(typename='std::string',
                               varname='str_val')
            with writer.gen_switch_block('val'):
                for enum_info in enum_list:
                    writer.write_line(f'case {enum_info.cval}: str_val = "{enum_info.strname}"; break;')
                if none_value is not None:
                    writer.write_line(f'case {none_value}: str_val = "None"; break;')
        self.add_repr(func_body=reprfunc)

        def richcmpfunc(writer):
            with writer.gen_if_block(f'{self.pyclassname}::Check(self) && {self.pyclassname}::Check(other)'):
                self.gen_ref_conv(writer, objname='self', refname='val1')
                self.gen_ref_conv(writer, objname='other', refname='val2')
                with writer.gen_if_block('op == Py_EQ'):
                    writer.gen_return_py_bool('val1 == val2')
                with writer.gen_if_block('op == Py_NE'):
                    writer.gen_return_py_bool('val1 != val2')
            writer.gen_return_py_notimplemented()
        self.add_richcompare(func_body=richcmpfunc)

        def new_body(writer):
            writer.gen_return_pyobject(self.pyclassname, 'val')
        self.add_new(func_body=new_body,
                     arg_list=[ObjConvArg(cvartype=f'{self.classname}',
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
            writer.gen_vardecl(typename='PyObject*',
                               varname='obj',
                               initializer='nullptr')
            with writer.gen_switch_block('val'):
                for enum in enum_list:
                    writer.write_line(f'case {enum.cval}: obj = Const_{enum.pyname}; break;')
                if none_value is not None:
                    writer.write_line(f'case {none_value}: Py_RETURN_NONE;')
            with writer.gen_if_block('obj == nullptr'):
                writer.gen_value_error('"invalid string for PrimType"')
            writer.write_line('Py_INCREF(obj);')
            writer.gen_return('obj')
        self.add_conv(conv_body)

        def deconv_body(writer):
            writer.gen_vardecl(typename='std::string',
                               varname='str_val');
            with writer.gen_if_block('PyString::FromPyObject(obj, str_val)'):
                first = True
                for enum in enum_list:
                    if ignore_case:
                        condition = f'strcasecmp(str_val.c_str(), "{enum.strname}") == 0'
                    else:
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
            self.gen_raw_conv(writer)
            writer.gen_return('false')
        self.add_deconv(deconv_body, extra_func=extra_deconv)
