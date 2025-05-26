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
                 pchar,
                 vardef,
                 varref):
        self.name = name
        self.pchar = pchar
        self.vardef = vardef
        self.varref = varref

    def gen_conv(self, gen):
        pass


class OptArg(ArgBase):
    """以降がオプション引数であることを示すマーカー
    """

    def __init__(self):
        super().__init__(pchar='|',
                         vardef=None,
                         varref=None)


class KwdArg(ArgBase):
    """以降がオプション引数であることを示すマーカー
    """

    def __init__(self):
        super().__init__(pchar='$',
                         vardef=None,
                         varref=None)


class RawArg(ArgBase):
    """PyArg_Parse で直接変換するタイプの引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 pchar,
                 cvartype,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         pchar=pchar,
                         vardef=make_vardef(cvartype, cvarname, cvardefault),
                         varref=make_varref(cvarname))


class IntArg(RawArg):
    """int 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         pchar='i',
                         cvartype='int',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class Int32Arg(RawArg):
    """std::int32_t 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         pchar='l',
                         cvartype='std::int32_t',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class Int64Arg(RawArg):
    """int 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         pchar='L',
                         cvartype='std::int64_t',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class UintArg(RawArg):
    """unsigned int 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         pchar='I',
                         cvartype='unsigned int',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class Uint32Arg(RawArg):
    """std::uint32_t 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         pchar='k',
                         cvartype='std::uint32_t',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class Uint64Arg(RawArg):
    """std::uint64_t 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         pchar='K',
                         cvartype='std::uint64_t',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class LongArg(RawArg):
    """long 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         pchar='l',
                         cvartype='long',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class UlongArg(RawArg):
    """unsigned long 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         pchar='k',
                         cvartype='unsigned long',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class DoubleArg(RawArg):
    """double 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault=None):
        super().__init__(name=name,
                         pchar='d',
                         cvartype='double',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class RawObjArg(RawArg):
    """PyObject* 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault='nullptr'):
        super().__init__(name=name,
                         pchar='O',
                         cvartype='PyObject*',
                         cvarname=cvarname,
                         cvardefault=cvardefault)


class TypedRawObjArg(ArgBase):
    """PyObject* 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault='nullptr',
                 pytypename):
        super().__init__(name=name,
                         pchar='O!',
                         vardef=f'PyObject* {cvarname} = nullptr',
                         varref=f'{pytypename}, &{cvarname}')


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
                 pchar,
                 cvartype,
                 cvarname,
                 cvardefault=None,
                 tmptype,
                 tmpname,
                 tmpdefault=None,
                 conv_func):
        super().__init__(name=name,
                         pchar=pchar,
                         vardef=make_vardef(tmptype, tmpname, tmpdefault),
                         varref=make_varref(tmpname))
        self.conv_func = conv_func

    def gen_conv(self, writer):
        self.conv_func(writer)


class BoolArg(ConvArg):
    """bool 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault=None):
        tmpname = f'{cvarname}_tmp'

        class MyConvFunc(ConvFunc):

            def __init__(self, *,
                         cvarname,
                         cvardefault):
                super().__init__(cvartype='bool',
                                 cvarname=cvarname,
                                 cvardefault=cvardefault)

            def conv_body(self, writer):
                with writer.gen_if_block(f'{tmpname} != -1'):
                    writer.gen_assign(self.cvarname, tmpname, casttype='bool')

        super().__init__(name=name,
                         pchar='p',
                         cvartype='bool',
                         cvarname=cvarname,
                         cvardefault=cvardefault,
                         tmptype='int',
                         tmpname=tmpname,
                         tmpdefault='-1',
                         conv_func=MyConvFunc(cvarname=cvarname,
                                              cvardefault=cvardefault))


class StringArg(ConvArg):
    """string 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvarname,
                 cvardefault=None):
        tmpname = f'{cvarname}_tmp'

        class MyConvFunc(ConvFunc):

            def __init__(self, *,
                         cvarname,
                         cvardefault):
                super().__init__(cvartype='std::string',
                                 cvarname=cvarname,
                                 cvardefault=cvardefault)

            def conv_body(self, writer):
                with writer.gen_if_block(f'{tmpname} != nullptr'):
                    writer.gen_assign(f'{self.cvarname}',
                                      f'std::string({tmpname})')

        super().__init__(name=name,
                         pchar='s',
                         cvartype='std::string',
                         cvarname=cvarname,
                         cvardefault=cvardefault,
                         tmptype='const char*',
                         tmpname=tmpname,
                         tmpdefault='nullptr',
                         conv_func=MyConvFunc(cvarname=cvarname,
                                              cvardefault=cvardefault))


class ObjConvArgBase(ArgBase):
    """PyObject* 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvartype,
                 cvarname,
                 cvardefault):
        tmptype = 'PyObject*'
        tmpname = f'{cvarname}_obj'
        super().__init__(name=name,
                         pchar='O',
                         vardef=make_vardef(tmptype, tmpname, 'nullptr'),
                         varref=make_varref(tmpname))
        self.cvartype = cvartype
        self.cvarname = cvarname
        self.cvardefault = cvardefault
        self.tmpname = tmpname

    def gen_conv(self, writer):
        line = make_vardef(self.cvartype, self.cvarname, self.cvardefault) + ';'
        writer.write_line(line)
        with writer.gen_if_block(f'{self.tmpname} != nullptr'):
            self.conv_body(writer)

    def conv_body(self, writer):
        raise ValueError('You must overwrite this code')


class ObjConvArg(ObjConvArgBase):
    """PyObject* 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvartype,
                 cvarname,
                 cvardefault,
                 pyclassname):
        super().__init__(name=name,
                         cvartype=cvartype,
                         cvarname=cvarname,
                         cvardefault=cvardefault)
        self.pyclassname = pyclassname

    def conv_body(self, writer):
        with writer.gen_if_block(f'!{self.pyclassname}::FromPyObject({self.tmpname}, {self.cvarname})'):
            writer.gen_value_error(f'"could not convert to {self.cvartype}"')


class TypedObjConvArg(ArgBase):
    """PyObject* 型の引数を表すクラス
    """

    def __init__(self, *,
                 name=None,
                 cvartype,
                 cvarname,
                 cvardefault,
                 pyclassname):
        tmptype = 'PyObject*'
        tmpname = f'{cvarname}_obj'
        super().__init__(name=name,
                         pchar='O!',
                         vardef=make_vardef(tmptype, tmpname, 'nullptr'),
                         varref=f'{pyclassname}::_typeobject(), &{tmpname}')
        self.cvartype = cvartype
        self.cvarname = cvarname
        self.cvardefault = cvardefault
        self.pyclassname = pyclassname
        self.tmpname = tmpname

    def gen_conv(self, writer):
        line = make_vardef(self.cvartype, self.cvarname, self.cvardefault) + ';'
        writer.write_line(line)
        with writer.gen_if_block(f'{self.tmpname} != nullptr'):
            with writer.gen_if_block(f'!{self.pyclassname}::FromPyObject({self.tmpname}, {self.cvarname})'):
                writer.gen_type_error(f'"could not convert to {self.cvartype}"')
