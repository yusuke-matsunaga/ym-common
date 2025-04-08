#! /usr/bin/env python3

""" Arg の定義ファイル

:file: arg.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""


def make_vardef(vartype, varname, vardefault):
    vardef = f'{vartype} {varname}'
    if vardefault is not None:
        vardef += f' = {vardefault}'
    return vardef

def make_varref(varname):
    return f'&{varname}'

    
class ArgBase:
    """引数の基底クラス
    """

    def __init__(self, *,
                 name=None,
                 option=False,
                 pchar,
                 vardef,
                 varref):
        self.name = name
        self.option = option
        self.pchar = pchar
        self.vardef = vardef
        self.varref = varref
    
    def gen_conv(self, gen):
        pass


class RawArg(ArgBase):
    """PyArg_Parse で直接変換するタイプの引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 option=False,
                 pchar,
                 cvartype,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         option=option,
                         pchar=pchar,
                         vardef=make_vardef(cvartype, cvarname, cvardefault),
                         varref=make_varref(cvarname))

    
class IntArg(RawArg):
    """int 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         option=option,
                         pchar='i',
                         cvartype='int',
                         cvarname=cvarname,
                         cvardefault=cvardefault)

    
class UintArg(RawArg):
    """unsigned int 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         option=option,
                         pchar='I',
                         cvartype='unsigned int',
                         cvarname=cvarname,
                         cvardefault=cvardefault)

    
class LongArg(RawArg):
    """long 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         option=option,
                         pchar='l',
                         cvartype='long',
                         cvarname=cvarname,
                         cvardefault=cvardefault)

    
class UlongArg(RawArg):
    """unsigned long 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         option=option,
                         pchar='k',
                         cvartype='unsigned long',
                         cvarname=cvarname,
                         cvardefault=cvardefault)

    
class DoubleArg(RawArg):
    """double 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         option=option,
                         pchar='d',
                         cvartype='double',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class RawObjArg(RawArg):
    """PyObject* 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvardefault='nullptr'):
        super().__init__(name=name,
                         option=option,
                         pchar='O',
                         cvartype='PyObject*',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class ConvFunc:
    """変換を行う関数
    """
    
    def __init__(self,
                 cvartype,
                 cvarname,
                 cvardefault):
        self.cvartype = cvartype
        self.cvarname = cvarname
        self.cvardefault = cvardefault
        
    def __call__(self, writer):
        line = make_vardef(self.cvartype, self.cvarname, self.cvardefault) + ';'
        writer.write_line(line)
        self.conv_body(writer)

        
class ConvArg(ArgBase):
    """一旦読み込んだ値を変換するタイプの引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 option=False,
                 pchar,
                 cvartype,
                 cvarname,
                 cvardefault=None,
                 tmptype,
                 tmpname,
                 tmpdefault=None,
                 conv_func):
        super().__init__(name=name,
                         option=option,
                         pchar=pchar,
                         vardef=make_vardef(tmptype, tmpname, tmpdefault),
                         varref=make_varref(tmpname))
        self.conv_func = conv_func

    def gen_conv(self, writer):
        self.conv_func(writer)
        

class BoolArg(ConvArg):
    """bool 型の引数を表すクラス
    """

    @staticmethod
    def make_tmpname(cvarname):
        return f'{cvarname}_tmp'
    
    class ConvFunc(ConvFunc):

        def __init__(self, *,
                     cvarname,
                     cvardefault):
            super().__init__(cvartype='bool',
                             cvarname=cvarname,
                             cvardefault=cvardefault)

        def conv_body(self, writer):
            tmpname = BoolArg.make_tmpname(self.cvarname)
            with writer.gen_if_block(f'{tmpname} != -1'):
                writer.gen_assign(self.cvarname, tmpname, casttype='bool')
                     
    def __init__(self, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvardefault=None):
        tmpname = BoolArg.make_tmpname(cvarname)
        super().__init__(name=name,
                         option=option,
                         pchar='p',
                         cvartype='bool',
                         cvarname=cvarname,
                         cvardefault=cvardefault,
                         tmptype='int',
                         tmpname=tmpname,
                         tmpdefault='-1',
                         conv_func=BoolArg.ConvFunc(cvarname=cvarname,
                                                    cvardefault=cvardefault))


class StringArg(ConvArg):
    """string 型の引数を表すクラス
    """

    @staticmethod
    def make_tmpname(cvarname):
        return f'{cvarname}_tmp'
    
    class ConvFunc(ConvFunc):

        def __init__(self, *,
                     cvarname,
                     cvardefault):
            super().__init__(cvartype='std::string',
                             cvarname=cvarname,
                             cvardefault=cvardefault)

        def conv_body(self, writer):
            tmpname = StringArg.make_tmpname(self.cvarname)
            with writer.gen_if_block(f'{tmpname} != nullptr'):
                writer.gen_assign(f'{self.cvarname}',
                                  f'std::string({tmpname})')
            
    def __init__(self, *,
                 name=None,
                 option=False,
                 cvarname,
                 cvardefault=None):
        tmpname = StringArg.make_tmpname(cvarname)
        super().__init__(name=name,
                         option=option,
                         pchar='s',
                         cvartype='std::string',
                         cvarname=cvarname,
                         cvardefault=cvardefault,
                         tmptype='const char*',
                         tmpname=tmpname,
                         tmpdefault='nullptr',
                         conv_func=StringArg.ConvFunc(cvarname=cvarname,
                                                      cvardefault=cvardefault))
            

class ObjArg(ArgBase):
    """PyObject* 型の引数を表すクラス
    """
                             
    def __init__(self, *,
                 name=None,
                 option=False,
                 cvartype,
                 cvarname,
                 cvardefault,
                 pyclassname):
        tmptype = 'PyObject*'
        tmpname = f'{cvarname}_obj'
        super().__init__(name=name,
                         option=option,
                         pchar='O',
                         vardef=make_vardef(tmptype, tmpname, 'nullptr'),
                         varref=make_varref(tmpname))
        self.cvartype = cvartype
        self.cvarname = cvarname
        self.cvardefault = cvardefault
        self.tmpname = tmpname
        self.pyclassname = pyclassname
        
    def gen_conv(self, writer):
        line = make_vardef(self.cvartype, self.cvarname, self.cvardefault) + ';'
        writer.write_line(line)
        with writer.gen_if_block(f'{self.tmpname} != nullptr'):
            with writer.gen_if_block(f'!{self.pyclassname}::FromPyObject({self.tmpname}, {self.cvarname})'):
                writer.gen_type_error(f'"could not convert to {self.cvartype}"')
            

class TypedObjArg(ArgBase):
    """PyObject* 型の引数を表すクラス
    """
                             
    def __init__(self, *,
                 name=None,
                 option=False,
                 cvartype,
                 cvarname,
                 cvardefault,
                 pyclassname):
        tmptype = 'PyObject*'
        tmpname = f'{cvarname}_obj'
        super().__init__(name=name,
                         option=option,
                         pchar='O!',
                         vardef=make_vardef(tmptype, tmpname, 'nullptr'),
                         varref=f'{pyclassname}::_typeobject(), &{tmpname}')
        self.cvartype = cvartype
        self.cvarname = cvarname
        self.cvardefault = cvardefault
        self.tmpname = tmpname
        
    def gen_conv(self, writer):
        line = make_vardef(self.cvartype, self.cvarname, self.cvardefault) + ';'
        writer.write_line(line)
        with writer.gen_if_block(f'{self.tmpname} != nullptr'):
            with writer.gen_if_block(f'!{self.pyclassname}::FromPyObject({self.tmpname}, {self.cvarname})'):
                writer.gen_type_error(f'could not convert to {self.cvartype}')
