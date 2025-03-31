#! /usr/bin/env python3

""" 関数定義を生成するクラス定義ファイル

:file: funcgen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from .utils import FuncDef, FuncDefWithArgs


class FuncBase:
    """関数の基本情報を表すクラス
    """

    def __init__(self, gen, name, body):
        self.gen = gen
        self.name = name
        self.body = body


class FuncWithArgs(FuncBase):
    """引数付きの関数の基本情報を表すクラス
    """

    def __init__(self, gen, name, body, arg_list):
        super().__init__(gen, name, body)
        self.arg_list = arg_list

        
class DeallocGen(FuncBase):
    """dealloc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body=None):
        if body is None:
            # デフォルト実装
            def default_body(writer):
                writer.write_line(f'obj->mVal.~{gen.classname}()')
            body = default_body
        self = super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(description=description,
                                   return_type='void',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_obj_conv(writer, varname='obj')
            self.body(writer)
            writer.write_line('PyTYPE(self)->tp_free(self)')


class ReprFuncGen(FuncBase):
    """reprfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)
            writer.gen_return_py_string('str_val')


class HashFuncGen(FuncBase):
    """hashfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(description=description,
                                   return_type='Py_hash_t',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)
            writer.gen_return_buildvalue('k', ['hash_val'])


class RichcmpFuncGen(FuncBase):
    """richcmpfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        super().__new__(cls, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'PyObject* other')
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.body(writer)


class InitProcGen(FuncWithArgs):
    """initproc 型の関数を生成するクラス
    """
    
    def __init__(cls, name, body, arg_list):
        super().__init__(gen, name, body, arg_list)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'PyObject* args',
                'PyObject* kwds')
        with writer.gen_func_block(desctiption=description,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            writer.gen_func_preamble(self.arg_list)
            self.body(writer)


class NewFuncGen(FuncWithArgs):
    """newfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body, arg_list):
        super().__init__(gen, name, body, arg_list)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyTypeObject* type',
                'PyObject* args',
                'PyObject* kwds')
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            writer.gen_func_preamble(self.arg_list)
            self.body(writer)


class LenFuncGen(FuncBase):
    """lenfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(description=description,
                                   return_type='Py_ssize_t',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)
            writer.gen_return_buildvalue('k', ['len_val'])


class InquiryGen(FuncBase):
    """inquiry 型の関数を生成するクラス
    """
    
    def __new__(self, gen, name, body):
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(description=description,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)


class UnaryFuncGen(FuncBase):
    """unaryfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)


class BinaryFuncGen(FuncBase):
    """binaryfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'PyObject* otehr')
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.body(writer)


class TernaryFuncGen(FuncBase):
    """ternaryfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'PyObject* obj2',
                'PyObject* obj3')
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.body(writer)


class SsizeArgFuncGen(FuncBase):
    """ssizeargfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'Py_ssize_t arg2')
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.body(writer)


class SsizeObjArgProcGen(FuncBase):
    """ssizeobjargproc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'Py_ssize_t arg2',
                'PyObject* arg3')
        with writer.gen_func_block(description=description,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            self.body(writer)


class ObjObjProcGen(FuncBase):
    """objobjproc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'PyObject* obj2')
        with writer.gen_func_block(description=description,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            self.body(writer)


class ObjObjArgProcGen(FuncBase):
    """objobjargproc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'PyObject* obj2',
                'PyObject* obj3')
        with writer.gen_func_block(description=description,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            self.body(writer)
