#! /usr/bin/env python3

""" CxxWriter のクラス定義ファイル

:file: cxxwriter.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

import re
from .utils import analyze_args


class CodeBlock:
    """字下げを行うコードブロックを表すクラス

    with 文の引数になることを仮定している．
    """

    def __init__(self, writer, *,
                 br_chars='{}',
                 prefix='',
                 postfix=''):
        self.__writer = writer
        self.__br_chars = br_chars
        self.__prefix = prefix
        self.__postfix = postfix

    def __enter__(self):
        line = f'{self.__prefix}{self.__br_chars[0]}'
        self.__writer.write_line(line)
        self.__writer.indent_inc()

    def __exit__(self, ex_type, ex_value, trace):
        self.__writer.indent_dec()
        line = f'{self.__br_chars[1]}{self.__postfix}'
        self.__writer.write_line(line)


class CxxWriter:
    """C++ のコードを出力するクラス
    """

    def __init__(self, *, fout):
        # 出力先のファイルオブジェクト
        self.__fout = fout

        # 現在のインデント位置
        self.__indent = 0

    def gen_include(self, filename):
        """include 文を出力する．

        :param str filename: ファイル名
        """
        if re.match('^<[^<>]*>$', filename):
            quote = ''
        else:
            quote = '"'
        line = f'#include {quote}{filename}{quote}'
        self.write_line(line)

    def gen_arg_parser(self, arg_list, *,
                       force_has_keywords=False,
                       is_proc=False):
        """引数を解釈する前処理のコードを生成する．
        """
        has_args, has_keywords = analyze_args(arg_list)
        if force_has_keywords:
            has_keywords = True
        if has_keywords:
            # キーワードテーブルの定義
            kwds_table = 'kwlist'
            with self.gen_array_block(typename='static const char*',
                                      arrayname=kwds_table,
                                      no_crlf=True):
                for arg in arg_list:
                    if arg.pchar == '|' or arg.pchar == '$':
                        continue
                    if arg.name is None:
                        self.write_line('"",')
                    else:
                        self.write_line(f'"{arg.name}",')
                self.write_line('nullptr')

        # パーズ結果を格納する変数の宣言
        for arg in arg_list:
            if arg.vardef is not None:
                line = f'{arg.vardef};'
                self.write_line(line)

        # PyArg_Parse() 用のフォーマット文字列の生成
        fmt_str = ""
        for arg in arg_list:
            fmt_str += arg.pchar

        # パーズ関数の呼び出し
        if has_args:
            if has_keywords:
                line = f'if ( !PyArg_ParseTupleAndKeywords(args, kwds, "{fmt_str}",'
                self.write_line(line)
                fpos = line.find('(')
                delta = line.find('(', fpos + 1) + 1
                self.indent_inc(delta)
                self.write_line(f'const_cast<char**>({kwds_table}),')
            else:
                line = f'if ( !PyArg_ParseTuple(args, "{fmt_str}",'
                self.write_line(line)
                fpos = line.find('(')
                delta = line.find('(', fpos + 1) + 1
                self.indent_inc(delta)
            nargs = len(arg_list)
            for i, arg in enumerate(arg_list):
                if arg.varref is None:
                    continue
                line = arg.varref
                if i < nargs - 1:
                    line += ','
                else:
                    line += ') ) {'
                self.write_line(line)
            self.indent_dec(delta)
            self.indent_inc()
            if is_proc:
                ret_val = '-1'
            else:
                ret_val = 'nullptr'
            self.gen_return(ret_val)
            self.indent_dec()
            self.write_line('}')
        elif force_has_keywords:
            self.gen_comment('余分な引数を取らないことを確認しておく．')
            line = 'if ( !PyArg_ParseTupleAndKeywords(args, kwds'
            line += f', "{fmt_str}"'
            line += f', const_cast<char**>({kwds_table})) ) {{'
            self.write_line(line)
            self.indent_inc()
            if is_proc:
                ret_val = '-1'
            else:
                ret_val = 'nullptr'
            self.gen_return(ret_val)
            self.indent_dec()
            self.write_line('}')

        # PyObject から C++ の変数へ変換する．
        for arg in arg_list:
            arg.gen_conv(self)

    def gen_sequence(self, sequence_gen, sequence_name):
        if sequence_gen is None:
            return
        sequence_gen(self, sequence_name)

    def gen_mapping(self, mapping_gen, mapping_name):
        if mapping_gen is None:
            return
        mapping_gen(self, mapping_name)

    def gen_vardecl(self, *,
                    typename,
                    varname,
                    initializer=None):
        """変数宣言を出力する．
        """
        line = f'{typename} {varname}'
        if initializer is not None:
            line += f' = {initializer}'
        line += ';'
        self.write_line(line)

    def gen_auto_assign(self, lval, rval, *,
                        casttype=None):
        """auto 宣言付きの代入文を出力する．
        """
        self.gen_assign(lval, rval, autodef=True, casttype=casttype)

    def gen_autoref_assign(self, lval, rval):
        """auto& 宣言付きの代入文を出力する．
        """
        self.gen_assign(lval, rval, autoref=True)

    def gen_assign(self, lval, rval, *,
                   autodef=False,
                   autoref=False,
                   casttype=None):
        """代入文を出力する．
        """
        if autodef:
            line = 'auto '
        elif autoref:
            line = 'auto& '
        else:
            line = ''
        line += f'{lval} = '
        if casttype is None:
            line += rval
        else:
            line += f'static_cast<{casttype}>({rval})'
        line += ';'
        self.write_line(line)

    def gen_stmt(self, stmt):
        self.write_line(f'{stmt};')

    def gen_return_buildvalue(self, fmt, val_list):
        """ Py_BuildValue() を用いた return 文を出力する．
        """
        line = f'return Py_BuildValue("{fmt}"'
        for val in val_list:
            line += f', {val}'
        line += ');'
        self.write_line(line)

    def gen_return(self, val):
        """return 文を出力する．
        """
        line = 'return'
        if val is not None:
            line += f' {val}'
        line += ';'
        self.write_line(line)

    def gen_return_py_int(self, expr):
        """int 値を表す PyObject を返す return 文を出力する．
        """
        self.gen_return_pyobject('PyInt', expr)

    def gen_return_py_long(self, expr):
        """long 値を表す PyObject を返す return 文を出力する．
        """
        self.gen_return_pyobject('PyLong', expr)

    def gen_return_py_float(self, expr):
        """float 値を表す PyObject を返す return 文を出力する．
        """
        self.gen_return_pyobject('PyFloat', expr)

    def gen_return_py_string(self, expr):
        """string 値を表す PyObject を返す return 文を出力する．
        """
        self.gen_return_pyobject('PyString', expr)

    def gen_return_py_bool(self, expr):
        """bool 値を表す PyObject を返す return 文を出力する．
        """
        self.gen_return(f'PyBool_FromLong({expr})')

    def gen_return_pyobject(self, pyclassname, expr):
        """PyObject に変換した値を返す return 文を出力する．
        """
        self.gen_return(f'{pyclassname}::ToPyObject({expr})')

    def gen_return_py_none(self):
        """Py_RETURN_NONE を出力する．
        """
        self.write_line('Py_RETURN_NONE;')

    def gen_return_py_notimplemented(self):
        """Py_RETURN_NOTIMPLEMENTED を出力する．
        """
        self.write_line('Py_RETURN_NOTIMPLEMENTED;')

    def gen_return_self(self, *, incref=False):
        """ return self; を出力する．
        """
        if incref:
            self.write_line('Py_XINCREF(self);')
        self.gen_return('self')

    def gen_goto(self, label):
        """ goto 文を出力する．
        """
        self.gen_stmt(f'goto {label}')

    def gen_label(self, label):
        """ ラベルを出力する．
        """
        self.indent_dec(1)
        self.write_line(f'{label}:')
        self.indent_inc(1)

    def gen_tp_alloc(self, *,
                     objclass,
                     typevar='type',
                     selfvar='self',
                     objvar='my_obj'):
        self.gen_auto_assign(f'{selfvar}', f'{typevar}->tp_alloc({typevar}, 0)')
        self.gen_auto_assign(f'{objvar}',
                             f'reinterpret_cast<{objclass}*>(self)')

    def gen_block(self, *,
                  no_crlf=False,
                  comment=None,
                  comments=None,
                  dox_comment=None,
                  dox_comments=None):
        """ブロックを出力する．
        """
        if not no_crlf:
            self.gen_CRLF()
        if comment is not None:
            self.gen_comment(comment)
        if comments is not None:
            for comment in comments:
                self.gen_comment(comment)
        if dox_comment is not None:
            self.gen_dox_comment(dox_comment)
        if dox_comments is not None:
            for comment in dox_comments:
                self.gen_dox_comment(comment)
        return CodeBlock(self)

    def gen_func_declaration(self, *,
                             no_crlf=False,
                             comment=None,
                             comments=None,
                             dox_comment=None,
                             dox_comments=None,
                             is_static=False,
                             return_type,
                             func_name,
                             args):
        """関数宣言を出力する．
        """
        self.gen_func_header(no_crlf=no_crlf,
                             comment=comment,
                             comments=comments,
                             dox_comment=dox_comment,
                             dox_comments=dox_comments,
                             is_static=is_static,
                             is_declaration=True,
                             return_type=return_type,
                             func_name=func_name,
                             args=args)

    def gen_func_header(self, *,
                        no_crlf=False,
                        comment=None,
                        comments=None,
                        dox_comment=None,
                        dox_comments=None,
                        is_static=False,
                        is_declaration,
                        return_type,
                        func_name,
                        args):
        """関数ヘッダを出力する．
        """
        if not no_crlf:
            self.gen_CRLF()
        if comment is not None:
            self.gen_comment(comment)
        if comments is not None:
            for comment in comments:
                self.gen_comment(comment)
        if dox_comment is not None:
            self.gen_dox_comment(dox_comment)
        if dox_comments is not None:
            for comment in dox_comments:
                self.gen_dox_comment(comment)
        if is_static:
            self.write_line('static')
        self.write_line(f'{return_type}')
        if is_declaration:
            postfix=';'
        else:
            postfix=''
        with CodeBlock(self,
                       br_chars='()',
                       prefix=func_name,
                       postfix=postfix):
            # 引数のリストを作る．
            # コメントがある時の処理がめんどくさい
            has_comments = False
            max_len = 0
            n = len(args)
            for i, arg in enumerate(args):
                if arg.comment is not None:
                    has_comments = True
                l = len(arg.body)
                if i < n - 1:
                    l += 1
                max_len = max(max_len, l)
            max_len += 1
            if has_comments:
                lines = []
                for i, arg in enumerate(args):
                    body = arg.body
                    if i < n - 1:
                        body += ','
                    if arg.comment is None:
                        line = body
                    else:
                        spc = ' ' * (max_len - len(body))
                        line = f'{body}{spc}///< {arg.comment}'
                    lines.append(line)
                self.write_lines(lines)
            else:
                lines = [arg.body for arg in args]
                self.write_lines(lines, delim=',')

    def gen_func_block(self, *,
                       no_crlf=False,
                       comment=None,
                       comments=None,
                       dox_comment=None,
                       dox_comments=None,
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
        self.gen_func_header(no_crlf=no_crlf,
                             comment=comment,
                             comments=comments,
                             dox_comment=dox_comment,
                             dox_comments=dox_comments,
                             is_static=is_static,
                             is_declaration=False,
                             return_type=return_type,
                             func_name=func_name,
                             args=args)
        return CodeBlock(self)

    def gen_if_block(self, condition):
        """if 文を出力する

        with obj.gen_if_block(condition):
          ...
        という風に用いる．
        """
        return CodeBlock(self,
                         prefix=f'if ( {condition} ) ')

    def gen_else_block(self):
        """else文を出力する

        with obj.gen_else_block():
          ...
        という風に用いる．
        """
        return CodeBlock(self,
                         prefix='else ')

    def gen_elseif_block(self, condition):
        """else if 文を出力する

        with obj.gen_elseif_block(condition):
          ...
        という風に用いる．
        """
        return CodeBlock(self,
                         prefix=f'else if ( {condition} ) ')

    def gen_switch_block(self, expr):
        """switch 文を出力する．

        with obj.gen_switch_block(expr):
          ...
        というふうに用いる．
        """
        return CodeBlock(self,
                         prefix=f'switch ( {expr} ) ')

    def gen_while_block(self, cond_expr):
        """while 文を出力する．
        """
        return CodeBlock(self,
                         prefix=f'while ( {cond_expr} ) ')

    def gen_for_block(self,
                      init_stmt,
                      cond_expr,
                      next_stmt):
        """for 文を出力する．
        """
        return CodeBlock(self,
                         prefix=f'for ( {init_stmt}; {cond_expr}; {next_stmt} ) ')

    def gen_array_block(self, *,
                        typename,
                        arrayname,
                        no_crlf=False,
                        comment=None,
                        comments=None,
                        dox_comment=None,
                        dox_comments=None):
        """initializer を持つ配列定義用ブロックを出力する．
        """
        if not no_crlf:
            self.gen_CRLF()
        if comment is not None:
            self.gen_comment(comment)
        if comments is not None:
            for comment in comments:
                self.gen_comment(comment)
        if dox_comment is not None:
            self.gen_dox_comment(dox_comment)
        if dox_comments is not None:
            for comment in dox_comments:
                self.gen_dox_comment(comment)
        return CodeBlock(self,
                         prefix=f'{typename} {arrayname}[] = ',
                         postfix=';')

    def gen_struct_block(self, structname, *,
                         no_crlf=False,
                         comment=None,
                         comments=None,
                         dox_comment=None,
                         dox_comments=None):
        """struct ブロックを出力する．
        """
        if not no_crlf:
            self.gen_CRLF()
        if comment is not None:
            self.gen_comment(comment)
        if comments is not None:
            for comment in comments:
                self.gen_comment(comment)
        if dox_comment is not None:
            self.gen_dox_comment(dox_comment)
        if dox_comments is not None:
            for comment in dox_comments:
                self.gen_dox_comment(comment)
        return CodeBlock(self,
                         prefix=f'struct {structname} ',
                         postfix=';')


    def gen_struct_init_block(self, *,
                              structname,
                              varname,
                              no_crlf=False,
                              comment=None,
                              comments=None,
                              dox_comment=None,
                              dox_comments=None):
        """struct の初期化用ブロックを出力する．
        """
        if not no_crlf:
            self.gen_CRLF()
        if comment is not None:
            self.gen_comment(comment)
        if comments is not None:
            for comment in comments:
                self.gen_comment(comment)
        if dox_comment is not None:
            self.gen_dox_comment(dox_comment)
        if dox_comments is not None:
            for comment in dox_comments:
                self.gen_dox_comment(comment)
        return CodeBlock(self,
                         prefix=f'{structname} {varname} = ',
                         postfix=';')

    def gen_try_block(self):
        """try ブロックを出力する．
        """
        return CodeBlock(self,
                         prefix='try ')

    def gen_catch_block(self, expr):
        """catch ブロックを出力する．
        """
        return CodeBlock(self,
                         prefix=f'catch ( {expr} ) ')

    def gen_catch_invalid_argument(self, msg=None, *,
                                   error_val='nullptr'):
        if msg is None:
            msg = '"invalid argument"'
        with self.gen_catch_block('std::invalid_argument err'):
            self.gen_vardecl(typename='std::ostringstream',
                             varname='buf')
            self.write_line(f'buf << {msg} << ": " << err.what();')
            self.gen_value_error(f'buf.str().c_str()',
                                 error_val=error_val)

    def gen_catch_out_of_range(self, msg=None):
        if msg is None:
            msg = '"out of range"'
        with self.gen_catch_block('std::out_of_range err'):
            self.gen_vardecl(typename='std::ostringstream',
                             varname='buf')
            self.write_line(f'buf << {msg} << ": " << err.what();')
            self.gen_value_error(f'buf.str().c_str()')

    def gen_type_error(self, error_msg, *,
                       noexit=False,
                       error_val='nullptr'):
        self.gen_error('PyExc_TypeError', error_msg,
                       noexit=noexit,
                       error_val=error_val)

    def gen_value_error(self, error_msg, *,
                        noexit=False,
                        error_val='nullptr'):
        self.gen_error('PyExc_ValueError', error_msg,
                       noexit=noexit,
                       error_val=error_val)

    def gen_error(self, error_type, error_msg, *,
                  noexit=False,
                  error_val='nullptr'):
        """エラー出力
        """
        self.write_line(f'PyErr_SetString({error_type}, {error_msg});')
        if not noexit:
            self.gen_return(error_val)

    def gen_dox_comments(self, comments):
        """Doxygen 用のコメントを出力する．
        """
        self.gen_comments(comment, doxygen=True)

    def gen_dox_comment(self, comment):
        """Doxygen 用のコメントを出力する．
        """
        self.gen_comment(comment, doxygen=True)

    def gen_comments(self, comments, *, doxygen=False):
        """コメントを出力する．
        """
        for comment in comments:
            self.gen_comment(comment, doxygen=doxygen)

    def gen_comment(self, comment, *, doxygen=False):
        """コメントを出力する．
        """
        if doxygen:
            line = '///'
        else:
            line = '//'
        if comment != '':
            line += f' {comment}'
        self.write_line(line)

    def gen_CRLF(self):
        """空行を出力する．
        """
        self.write_line('')

    def write_lines(self, lines, *,
                    delim=None):
        """複数行を出力する
        """
        n = len(lines)
        for i, line in enumerate(lines):
            if i < n - 1 and delim is not None:
                line += delim
            self.write_line(line)

    def write_line(self, line):
        """一行を出力する．
        """
        if line == '':
            self.__fout.write('\n')
        else:
            spc = ' ' * self.__indent
            self.__fout.write(f'{spc}{line}\n')

    def indent_inc(self, delta=2):
        """インデント量を増やす．
        """
        self.__indent += delta

    def indent_dec(self, delta=2):
        """インデント量を減らす
        """
        self.__indent -= delta

    def indent_set(self, val):
        """インデント量をセットする．
        """
        self.__indent = val
