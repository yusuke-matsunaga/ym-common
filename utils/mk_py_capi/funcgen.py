#! /usr/bin/env python3

""" 関数定義を生成するクラス定義ファイル

:file: funcgen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from .utils import FuncDef, FuncDefWithArgs


class DeallocGen(FuncDef):
    """dealloc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(description=description,
                                   return_type='void',
                                   func_name=self.name,
                                   args=args):
            self.func(writer)


class ReprFuncGen(FuncDef):
    """reprfunc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.func(writer)


class HashFuncGen(FuncDef):
    """hashfunc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(description=description,
                                   return_type='Py_hash_t',
                                   func_name=self.name,
                                   args=args):
            self.func(writer)


class RichcmpFuncGen(FuncDef):
    """richcmpfunc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'PyObject* other')
        with writer.gen_func_block(description=description,
                                 return_type='PyObject*',
                                 func_name=self.name,
                                 args=args):
            self.func(writer)


class InitProcGen(FuncDefWithArgs):
    """initproc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func, arg_list):
        self = super().__new__(cls, name, func, arg_list)
        return self

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
            self.func(writer)


class NewFuncGen(FuncDefWithArgs):
    """newfunc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func, arg_list):
        self = super().__new__(cls, name, func, arg_list)
        return self

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
            self.func(writer)


class LenFuncGen(FuncDef):
    """lenfunc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(description=description,
                                   return_type='Py_ssize_t',
                                   func_name=self.name,
                                   args=args):
            self.func(writer)


class InquiryGen(FuncDef):
    """inquiry 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(description=description,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            self.func(writer)


class UnaryFuncGen(FuncDef):
    """unaryfunc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.func(writer)


class BinaryFuncGen(FuncDef):
    """binaryfunc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'PyObject* otehr')
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.func(writer)


class TernaryFuncGen(FuncDef):
    """ternaryfunc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'PyObject* obj2',
                'PyObject* obj3')
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.func(writer)


class SsizeArgFuncGen(FuncDef):
    """ssizeargfunc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'Py_ssize_t arg2')
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.func(writer)


class SsizeObjArgProcGen(FuncDef):
    """ssizeobjargproc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'Py_ssize_t arg2',
                'PyObject* arg3')
        with writer.gen_func_block(description=description,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            self.func(writer)


class ObjObjProcGen(FuncDef):
    """objobjproc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'PyObject* obj2')
        with writer.gen_func_block(description=description,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            self.func(writer)


class ObjObjArgProcGen(FuncDef):
    """objobjargproc 型の関数を生成するクラス
    """
    
    def __new__(cls, name, func):
        self = super().__new__(cls, name, func)
        return self

    def __call__(self, writer, *,
                 description=None):
        args = ('PyObject* self',
                'PyObject* obj2',
                'PyObject* obj3')
        with writer.gen_func_block(description=description,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            self.func(writer)
