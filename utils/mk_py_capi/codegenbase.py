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

    def gen_declaration(self, typename, varname):
        """変数宣言を出力する．
        """
        self.__parent.gen_declaration(typename, varname);
        
    def gen_auto_assign(self, lval, rval):
        """auto 宣言付きの代入文を出力する．
        """
        self.__parent.gen_auto_assign(lval, rval)
        
    def gen_assign(self, lval, rval, *,
                   autodef=False):
        """代入文を出力する．
        """
        self.__parent.gen_assign(lval, rval, autodef=autodef)

    def gen_buildvalue_return(self, fmt, val_list):
        """ Py_BuildValue() を用いた return 文を出力する．
        """
        self.__parent.gen_buildvalue_return(fmt, val_list)
        
    def gen_return(self, val):
        """return 文を出力する．
        """
        self.__parent.gen_return(val)

    def gen_dox_comment(self, comment):
        """Doxygen 用のコメントを出力する．
        """
        self.__parent.gen_dox_comment(comment)
        
    def gen_comment(self, comment, *, doxygen=False):
        """コメントを出力する．
        """
        self.__parent.gen_comment(comment, doxygen=doxygen)
        
    def gen_CRLF(self):
        """空行を出力する．
        """
        self.__parent.gen_CRLF()

    def _write_line(self, line):
        self.__parent._write_line(line)

    def _indent_inc(self, delta=2):
        self.__parent._indent_inc(delta)

    def _indent_dec(self, delta=2):
        self.__parent._indent_dec(delta)

    def _indent_set(self, val):
        self.__parent._indent_set(val)
