#! /usr/bin/env python3

""" CodeGenBase の定義ファイル

MkBase を親として持つ．

:file: codegenbase.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

class CodeGenBase:

    def __init__(self, parent):
        self.__parent = parent

    @property
    def parent(self):
        return self.__parent
    
    @property
    def classname(self):
        return self.__parent.classname

    @property
    def pyclassname(self):
        return self.__parent.pyclassname

    @property
    def namespace(self):
        return self.__parent.namespace

    @property
    def typename(self):
        return self.__parent.typename

    @property
    def objectname(self):
        return self.__parent.objectname

    def _write_begin(self):
        self.__parent._write_begin()

    def _write_end(self):
        self.__parent._write_end()

    def _write_line(self, line):
        self.__parent._write_line(line)

    def _indent_inc(self, delta=2):
        self.__parent._indent_inc(delta)

    def _indent_dec(self, delta=2):
        self.__parent._indent_dec(delta)

    def _indent_set(self, val):
        self.__parent._indent_set(val)
