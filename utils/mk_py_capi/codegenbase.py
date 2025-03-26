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

    def gen_py_return_none(self):
        """Py_RETURN_NONE を出力する．
        """
        self.__parent.gen_py_return_none()
        
    def gen_func_declaration(self, *,
                             description=None,
                             is_static=False,
                             return_type,
                             func_name,
                             args):
        """関数宣言を出力する．
        """
        self.__parent.gen_func_declaration(descrition=description,
                                           is_static=is_static,
                                           return_type=return_type,
                                           func_name=func_name,
                                           args=args)

    def gen_func_header(self, *,
                        description=None,
                        is_static=False,
                        is_declaration,
                        return_type,
                        func_name,
                        args):
        """関数ヘッダを出力する．
        """
        self.__parent.gen_func_header(description=description,
                                      is_static=is_static,
                                      is_declaration=is_declaration,
                                      return_type=return_type,
                                      func_name=func_name,
                                      args=args)
        
    def gen_func_block(self, *,
                       description=None,
                       is_static=False,
                       return_type,
                       func_name,
                       args):
        """関数定義を出力する．

        with obj.gen_func_block(return_type=XX,
                                func_name=XX,
                                args=..):
          ...
        という風に用いる．
        """
        return self.__parent.gen_func_block(description=description,
                                            is_static=is_static,
                                            return_type=return_type,
                                            func_name=func_name,
                                            args=args)

    def gen_if_block(self, condition):
        """if 文を出力する

        with obj.gen_if_block(condition):
          ...
        という風に用いる．
        """
        return self.__parent.gen_if_block(condition)

    def gen_else_block(self):
        """else文を出力する

        with obj.gen_else_block():
          ...
        という風に用いる．
        """
        return self.__parent.gen_else_block()

    def gen_elseif_block(self, condition):
        """else if 文を出力する

        with obj.gen_elseif_block(condition):
          ...
        という風に用いる．
        """
        return self.__parent.gen_elseif_block(condition)

    def gen_array_block(self, *,
                        typename,
                        arrayname):
        """initializer を持つ配列定義用ブロックを出力する．
        """
        return self.__parent.gen_array_block(typename=typename, arrayname=arrayname)

    def gen_for_block(self,
                      init_stmt,
                      cond_expr,
                      next_stmt):
        """for 文を出力する．
        """
        return self.__parent.gen_for_block(init_stmt, cond_expr, next_stmt)

    def gen_struct_block(self, structname):
        """struct ブロックを出力する．
        """
        return self.__parent.gen_struct_block(structname)

    def gen_try_block(self):
        """try ブロックを出力する．
        """
        return self.__parent.gen_try_block()

    def gen_catch_block(self, expr):
        """catch ブロックを出力する．
        """
        return self.__parent.gen_catch_block(expr)
    
    def gen_type_error(self, error_msg):
        self.__parent.gen_type_error(error_msg)

    def gen_value_error(self, error_msg):
        self.__parent.gen_value_error(error_msg)
        
    def gen_error(self, error_type, error_msg):
        """エラー出力
        """
        self.gen_error(error_type, error_msg)

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
