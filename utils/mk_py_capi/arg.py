#! /usr/bin/env python3

""" Arg の定義ファイル

:file: arg.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi.codegenbase import CodeGenBase


class ArgBase(CodeGenBase):
    """引数の基底クラス
    """

    def __init__(self, parent, *,
                 name=None,
                 option=False,
                 pchar,
                 cvarname,
                 cvartype,
                 cvardefault=None):
        super().__init__(parent)
        self.name = name
        self.option = option
        self.pchar = pchar
        self.cvarname = cvarname
        self.cvartype = cvartype
        self.cvardefault = cvardefault
    
    def gen_conv(self):
        pass


class RawArg(ArgBase):
    """PyArg_Parse で直接変換するタイプの引数を表すクラス
    """

    def __init__(self, parent, *,
                 name=None,
                 option=False,
                 pchar,
                 cvarname,
                 cvartype,
                 cvardefault=None):
        super().__init__(parent,
                         name=name,
                         option=option,
                         pchar=pchar,
                         cvarname=cvarname,
                         cvartype=cvartype,
                         cvardefault=cvardefault)

    def gen_vardef(self):
        """変数の宣言を行う．
        """
        line = f'{self.cvartype} {self.cvarname}'
        if self.cvardefault is not None:
            line += f' = {self.cvardefault}'
        line += ';'
        self._write_line(line)

    def gen_varref(self):
        """PyArg_Parse() 用の変数の参照を返す．
        """
        return f'&{self.cvarname}'

    
class IntArg(RawArg):
    """int 型の引数を表すクラス
    """

    def __init__(self, parent, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvardefault=None):
        super().__init__(parent,
                         name=name,
                         option=option,
                         pchar='i',
                         cvartype='int',
                         cvarname=cvarname,
                         cvardefault=cvardefault)

    
class DoubleArg(RawArg):
    """double 型の引数を表すクラス
    """

    def __init__(self, parent, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvardefault=None):
        super().__init__(parent,
                         name=name,
                         option=option,
                         pchar='d',
                         cvartype='double',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class ConvArg(ArgBase):
    """一旦読み込んだ値を変換するタイプの引数を表すクラス
    """

    def __init__(self, parent, *,
                 name=None,
                 option=False,
                 pchar,
                 cvarname,
                 cvartype,
                 cvardefault=None,
                 tmpname=None,
                 tmptype,
                 tmpdefault=None):
        super().__init__(parent,
                         name=name,
                         option=option,
                         pchar=pchar,
                         cvarname=cvarname,
                         cvartype=cvartype,
                         cvardefault=cvardefault)
        if tmpname is None:
            tmpname = f'{cvarname}_tmp'
        self.tmpname = tmpname
        self.tmptype = tmptype
        self.tmpdefault = tmpdefault

    def gen_vardef(self):
        """変数の宣言を行う．
        """
        line = f'{self.tmptype} {self.tmpname}'
        if self.tmpdefault is not None:
            line += f' = {self.tmpdefault}'
        line += ';'
        self._write_line(line)

    def gen_varref(self):
        """PyArg 用の変数参照を返す．
        """
        return f'&{self.tmpname}'

    def gen_conv(self):
        line = f'{self.cvartype} {self.cvarname}'
        if self.cvardefault is not None:
            line += f' = {self.cvardefault}'
        line += ';'
        self._write_line(line)
        self.gen_conv_body()
        

class BoolArg(ConvArg):
    """bool 型の引数を表すクラス
    """

    def __init__(self, parent, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvardefault=None):
        super().__init__(parent,
                         name=name,
                         option=option,
                         pchar='p',
                         cvartype='bool',
                         cvarname=cvarname,
                         cvardefault=cvardefault,
                         tmptype='int',
                         tmpdefault='-1')

    def gen_conv_body(self):
        with self.gen_if_block(f'{self.tmpname} != -1'):
            self.gen_assign(f'{self.cvarname}',
                            f'static_cast<bool>({self.tmpname})')


class StringArg(ConvArg):
    """string 型の引数を表すクラス
    """

    def __init__(self, parent, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvardefault=None):
        super().__init__(parent,
                         name=name,
                         option=option,
                         pchar='s',
                         cvartype='std::string',
                         cvarname=cvarname,
                         cvardefault=cvardefault,
                         tmptype='const char*',
                         tmpdefault='nullptr')

    def gen_conv_body(self):
        with self.gen_if_block(f'{self.tmpname} != nullptr'):
            self.gen_assign(f'{self.cvarname}',
                            f'std::string({self.tmpname})')


class ObjArg(ConvArg):
    """PyObject* 型の引数を表すクラス
    """

    def __init__(self, parent, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvartype,
                 cvardefault=None):
        super().__init__(parent,
                         name=name,
                         option=option,
                         pchar='O',
                         cvarname=cvarname,
                         cvartype=cvartype,
                         cvardefault=cvardefault,
                         tmptype='PyObject*',
                         tmpdefault='nullptr')
        
    def gen_conv_body(self):
        with self.gen_if_block(f'{self.tmpname} != nullptr'):
            self.gen_obj_conv()
            

class TypedObjArg(ConvArg):
    """PyObject* 型の引数を表すクラス
    """

    def __init__(self, parent, *,
                 name=None,
                 option=False,
                 ptype,
                 cvarname,
                 cvartype):
        super().__init__(parent,
                         name=name,
                         option=option,
                         pchar='O!',
                         ptype=ptype,
                         cvarname=cvarname,
                         cvartype=cvartype,
                         cvarefault=cvardefault,
                         tmptype='PyObject*',
                         tmpdefault='nullptr')

    def gen_varref(self):
        return f'{self.ptype}, &{self.tmpname}'
        
    def gen_conv_body(self):
        with self.gen_if_block(f'{self.tmpname} != nullptr'):
            with self.gen_if_block(f'!{self.pyclassname}::FromPyObject({self.tmpname}, {self.cvarname})'):
                self.gen_type_error(f'could not convert to {self.classname}')
                self.gen_return('nullptr')
