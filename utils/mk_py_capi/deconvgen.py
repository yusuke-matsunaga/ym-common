#! /usr/bin/env python3

""" DeconvGen の定義ファイル

:file: deconvgen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi.codegenbase import CodeGenBase
from mk_py_capi.codeblock import FuncBlock, IfBlock


class DeconvGen(CodeGenBase):

    def __init__(self, parent):
        super().__init__(parent)

    def __call__(self):
        with FuncBlock(self.parent,
                       description='PyObject を {self.classname} に変換する．',
                       return_type='bool',
                       func_name=f'{self.pyclassname}::Deconv::operator()',
                       args=('PyObject* obj',
                             f'{self.classname}& val')):
            with IfBlock(self.parent,
                         condition=f'{self.pyclassname}::Check(val)'):
                self._write_line(f'val = {self.pyclassname}::_get_ref(obj);')
            self._write_line('return false;')

