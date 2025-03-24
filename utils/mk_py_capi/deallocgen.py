#! /usr/bin/env python3

""" DeallocGen の定義ファイル

:file: deallocgen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi.codegenbase import CodeGenBase
from mk_py_capi.codeblock import FuncBlock


class DeallocGen(CodeGenBase):

    def __init__(self, parent):
        super().__init__(parent)

    def __call__(self, func_name):
        with FuncBlock(self.parent,
                       description='終了関数',
                       return_type='void',
                       func_name=func_name,
                       args=(('PyObject* self', ))):
            self._write_line(f'auto obj = reinterpret_cast<{self.objectname}*>(self);')
            self.bodygen()
            self._write_line('PyTYPE(self)->tp_free(self)')

    def bodygen(self):
        self._write_line(f'obj->mVal.~{self.classname}()')
        
