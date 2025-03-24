#! /usr/bin/env python3

""" ConvGen のクラス定義

クラス T が T(const T& src) の形のコンストラクタ(コピーコンストラクタ)
を持っていれば正しく動く
  
:file: convgen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi.codegenbase import CodeGenBase
from mk_py_capi.codeblock import FuncBlock


class ConvGen(CodeGenBase):

    def __init__(self, parent):
        super().__init__(parent)
        
    def __call__(self):
        with FuncBlock(self.parent,
                       description=f'{self.classname} を PyObject に変換する．',
                       return_type='PyObject*',
                       func_name=f'{self.pyclassname}::Conv::operator()',
                       args=(f'const {self.classname}& val', )):
            self._write_line(f'auto type = {self.pyclassname}::_typeobject();')
            self._write_line('auto obj = type->tp_alloc(type, 0);')
            self._write_line(f'auto obj1 = reinterpret_cast<{self.objectname}*>(obj);')
            self._write_line(f'new (&obj1->mVal) {self.classname}(val);')
            self._write_line('return obj;')
