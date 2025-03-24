#! /usr/bin/env python3

""" CodeBlock の定義ファイル

:file: codeblock.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi.codegenbase import CodeGenBase


class CodeBlock(CodeGenBase):

    def __init__(self, parent, *,
                 br_chars='{}',
                 prefix='',
                 postfix=''):
        super().__init__(parent)
        self.__br_chars = br_chars
        self.__prefix = prefix
        self.__postfix = postfix

    def __enter__(self):
        self.before_enter()
        line = f'{self.__prefix}{self.__br_chars[0]}'
        self._write_line(line)
        self._indent_inc()

    def __exit__(self, ex_type, ex_value, trace):
        self._indent_dec()
        line = f'{self.__br_chars[1]}{self.__postfix}'
        self._write_line(line)
        self.after_exit()

    def before_enter(self):
        pass

    def after_exit(self):
        pass

    
class FuncBlock(CodeBlock):

    def __init__(self, parent, *,
                 description=None,
                 return_type,
                 func_name,
                 args):
        super().__init__(parent)
        self.description=description
        self.return_type=return_type
        self.func_name = func_name
        self.args = args
        
    def before_enter(self):
        self._write_line('') # 空行
        if self.description is not None:
            self._write_line(f'// @brief {self.description}')
        self._write_line(f'{self.return_type}')
        with CodeBlock(self.parent,
                       br_chars='()',
                       prefix=self.func_name):
            nargs = len(self.args)
            for i, arg in enumerate(self.args):
                line = arg
                if i < nargs - 1:
                    line += ','
                self._write_line(line)


class IfBlock(CodeBlock):

    def __init__(self, parent, *,
                 condition):
        super().__init__(parent,
                         prefix=f'if ( {condition} ) ')


class ElseBlock(CodeBlock):

    def __init__(self, parent):
        super().__init__(parent,
                         prefix='else ')

        
class ElseIfBlock(CodeBlock):

    def __init__(self, parent, *,
                 condition):
        super().__init__(parent,
                         prefix=f'else if ( {condition} ) ')
        
class ArrayBlock(CodeBlock):

    def __init__(self, parent, *,
                 typename,
                 arrayname):
        super().__init__(parent,
                         prefix=f'{typename} {arrayname}[] = ',
                         postfix=';')

