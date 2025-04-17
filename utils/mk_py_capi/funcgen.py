#! /usr/bin/env python3

""" 関数定義を生成するクラス定義ファイル

:file: funcgen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

def mk_varname(varname, unused=False):
    if unused:
        return f'Py_UNUSED({varname})'
    return varname


class CArg:

    def __init__(self, body, *,
                 comment=None):
        self.body = body
        self.comment = comment

    @staticmethod
    def GenArg(typename, varname, *,
               comment=None):
        return CArg(f'{typename} {varname}',
                    comment=comment)

    @staticmethod
    def PyArg(varname, *,
              comment=None):
        return CArg.GenArg('PyObject*', varname,
                           comment=comment)

    @staticmethod
    def Self(*,
             unused=False,
             comment=None):
        varname = mk_varname('self', unused)
        return CArg.PyArg(varname, comment=comment)

    @staticmethod
    def Args(*,
             unused=False,
             comment=None):
        varname = mk_varname('args', unused)
        return CArg.PyArg(varname, comment=comment)

    @staticmethod
    def Kwds(*,
             comment=None):
        return CArg.PyArg('kwds', comment=comment)

    @staticmethod
    def Other(*,
              unused=False,
              comment=None):
        varname = mk_varname('other', unused)
        return CArg.PyArg(varname, comment=comment)

    @staticmethod
    def Type(*,
             comment=None):
        return CArg.GenArg('PyTypeObject*', 'type',
                           comment=comment)

    @staticmethod
    def Closure(*,
                unused=False,
                comment=None):
        varname = mk_varname('closure', unused)
        return CArg.GenArg('void*', varname,
                           comment=comment)


class FuncBase:
    """関数の基本情報を表すクラス
    """

    def __init__(self, gen, name, tp_name, body):
        self.gen = gen
        self.name = name
        self.tp_name = tp_name
        self.body = body

    def gen_tp(self, writer):
        writer.gen_assign(f'{self.gen.typename}.tp_{self.tp_name}',
                          f'{self.name}')


class FuncWithArgs(FuncBase):
    """引数付きの関数の基本情報を表すクラス
    """

    def __init__(self, gen, name, tp_name, body, arg_list):
        super().__init__(gen, name, tp_name, body)
        self.arg_list = arg_list


class DeallocGen(FuncBase):
    """dealloc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body):
        if body == 'default':
            # デフォルト実装
            def default_body(writer):
                writer.write_line(f'obj->mVal.~{gen.classname}();')
            body = default_body
        self = super().__init__(gen, name, 'dealloc', body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = [CArg.Self()]
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='void',
                                   func_name=self.name,
                                   args=args):
            if self.body is not None:
                self.gen.gen_obj_conv(writer, varname='obj')
                self.body(writer)
            writer.write_line('Py_TYPE(self)->tp_free(self);')


class ReprFuncGen(FuncBase):
    """reprfunc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body, tp_name='repr'):
        if body is None:
            # 空
            def null_body(writer):
                writer.gen_comment("val を表す文字列を str_val に入れる．")
            body = null_body
        elif body == 'sample':
            # sample 実装
            def sample_body(writer):
                writer.gen_comment("このコードは実際には機能しない．")
                writer.gen_auto_assign('str_val', 'val.repr_str()')
            body = sample_body
        super().__init__(gen, name, tp_name, body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = [CArg.Self()]
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
                writer.gen_return_py_string('str_val')
            writer.gen_catch_invalid_argument()


class StrFuncGen(ReprFuncGen):
    """str() 用の reprfunc を生成するクラス
    """

    def __init__(self, gen, name, body):
        super().__init__(gen, name, body, 'str')


class HashFuncGen(FuncBase):
    """hashfunc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body):
        if body is None:
            # 空
            def null_body(writer):
                writer.gen_comment("val のハッシュ値を返す．")
            body = null_body
        elif body == 'sample':
            # sample 実装
            def sample_body(writer):
                writer.gen_comment("このコードは実際には機能しない．")
                writer.gen_auto_assign('hash_val', 'val.hash()')
            body = sample_body
        super().__init__(gen, name, 'hash', body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = [CArg.Self()]
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='Py_hash_t',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
            writer.gen_catch_invalid_argument(error_val='0')


class CallFuncGen(FuncWithArgs):
    """callfunc(ternaryfunc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body, arg_list, *,
                 arg2name='args',
                 arg3name='kwds'):
        if body is None:
            # 空
            def null_body(writer):
                writer.gen_comment('args, kwds を解釈して結果を返す．')
            body = null_body
        super().__init__(gen, name, 'call', body, arg_list)
        self.__args = [CArg.Self(),
                       CArg.PyArg(arg2name),
                       CArg.PyArg(arg3name)]

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=self.__args):
            writer.gen_func_preamble(self.arg_list)
            self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
            writer.gen_catch_invalid_argument()


class RichcmpFuncGen(FuncBase):
    """richcmpfunc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body):
        if body == 'eq_default':
            def cmp_func(writer):
                with writer.gen_if_block(f'{gen.pyclassname}::Check(other)'):
                    gen.gen_ref_conv(writer, objname='other', refname='val2')
                    with writer.gen_if_block('op == Py_EQ'):
                        writer.gen_return_py_bool('val == val2')
                    with writer.gen_if_block('op == Py_NE'):
                        writer.gen_return_py_bool('val != val2')
                writer.gen_return_py_notimplemented()
            body = cmp_func
        elif body == 'cmp_default':
            def cmp_func(writer):
                with writer.gen_if_block(f'{gen.pyclassname}::Check(other)'):
                    gen.gen_ref_conv(writer, objname='other', refname='val2')
                    writer.write_line('Py_RETURN_RICHCOMPARE(val, val2, op);')
                writer.gen_return_py_notimplemented()
            body = cmp_func
        elif body is None:
            # 空
            def null_body(writer):
                writer.gen_comments(['self と other を比較して結果のブール値を表す PyObject* を返す．',
                                     'op の値は Py_LT, Py_LE, Py_EQ, Py_NE, Py_GT, Py_GE のいずれか．',
                                     'サポートしていない演算の場合は Py_RETURN_NOTIMPLEMETED を返す．'])
            body = null_body
        super().__init__(gen, name, 'richcompare', body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = [CArg.Self(),
                CArg.PyArg('other'),
                CArg.GenArg('int', 'op')]
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
            writer.gen_catch_invalid_argument()


class InitProcGen(FuncWithArgs):
    """initproc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body, arg_list):
        if body is None:
            # 空
            def null_body(writer):
                writer.gen_comments(['self を args, kwds の内容に従って初期化する．',
                                     '成功したら 0 を返す．',
                                     '失敗したら例外をセットして -1 を返す．'])
            body = null_body
        super().__init__(gen, name, 'init', body, arg_list)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = [CArg.Self(),
                CArg.Args(),
                CArg.Kwds()]
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            writer.gen_func_preamble(self.arg_list, is_proc=True)
            with writer.gen_try_block():
                self.body(writer)
            writer.gen_catch_invalid_argument(error_val='-1')


class NewFuncGen(FuncWithArgs):
    """newfunc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body, arg_list):
        self.__disabled = False
        if body == 'default':
            # デフォルト実装
            def default_body(writer):
                writer.gen_auto_assign('self', 'type->tp_alloc(type, 0)')
                writer.gen_return_self()
            body = default_body
        elif body == 'disabled':
            # 禁止
            self.__disabled = True
        elif body == 'sample':
            # sample 実装
            def sample_body(writer):
                writer.gen_comment('この関数は実際には機能しない．')
                writer.gen_auto_assign('self', 'type->tp_alloc(type, 0)')
                gen.gen_obj_conv(writer, varname='my_obj')
                writer.write_line(f'new (&myobj->mVal) {gen.classname}()')
                writer.gen_return_self()
            body = sample_body
        super().__init__(gen, name, 'new', body, arg_list)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = [CArg.Type(),
                CArg.Args(),
                CArg.Kwds()]
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            if self.__disabled:
                msg = f'"instantiation of \'{self.gen.classname}\' is disabled"'
                writer.gen_type_error(msg)
            else:
                writer.gen_func_preamble(self.arg_list, force_has_keywords=True)
                with writer.gen_try_block():
                    self.body(writer)
                writer.gen_catch_invalid_argument()


class LenFuncGen(FuncBase):
    """lenfunc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        elif body == 'sample':
            # sample 実装
            def sample_body(writer):
                writer.gen_comment('val のサイズ(len) を len_val に入れる．')
                writer.gen_comment('このコードは実際には機能しない．')
                writer.gen_auto_assign('len_val', 'val.len()')
            body = sample_body
        super().__init__(gen, name, None, body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = [CArg.Self()]
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='Py_ssize_t',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
                writer.gen_return('len_val')
            writer.gen_catch_invalid_argument(error_val='-1')


class InquiryGen(FuncBase):
    """inquiry 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, None, body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = [CArg.Self()]
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
                writer.gen_return('inquiry_val')
            writer.gen_catch_invalid_argument(error_val='-1')


class UnaryFuncGen(FuncBase):
    """unaryfunc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, None, body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = [CArg.Self()]
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
            writer.gen_catch_invalid_argument()


class BinaryFuncGen(FuncBase):
    """binaryfunc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body, *,
                 arg2name=None):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, None, body)
        if arg2name is None:
            arg2name = 'other'
        self.__args = [CArg.Self(),
                       CArg.PyArg(arg2name)]

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=self.__args):
            self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
            writer.gen_catch_invalid_argument()


class TernaryFuncGen(FuncBase):
    """ternaryfunc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body, *,
                 arg2name=None,
                 arg3name=None,
                 has_ref_conv=True):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, None, body)
        if arg2name is None:
            arg2name = 'obj2'
        if arg3name is None:
            arg3name = 'obj3'
        self.__args = [CArg.Self(),
                       CArg.PyArg(arg2name),
                       CArg.PyArg(arg3name)]
        self.__has_ref_conv = has_ref_conv

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=self.__args):
            if self.__has_ref_conv:
                self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
            writer.gen_catch_invalid_argument()


class SsizeArgFuncGen(FuncBase):
    """ssizeargfunc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body, *,
                 arg2name=None):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, None, body)
        if arg2name is None:
            arg2name = 'arg2'
        self.__args = [CArg.Self(),
                       CArg.GenArg('Py_ssize_t', arg2name)]

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=self.__args):
            self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
            writer.gen_catch_invalid_argument()


class SsizeObjArgProcGen(FuncBase):
    """ssizeobjargproc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body, *,
                 arg2name=None,
                 arg3name=None):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, None, body)
        if arg2name is None:
            arg2name = 'arg2'
        if arg3name is None:
            arg3name = 'arg3'
        self.__args = [CArg.Self(),
                       CArg.GenArg('Py_ssize_t', arg2name),
                       CArg.PyArg(arg3name)]

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='int',
                                   func_name=self.name,
                                   args=self.__args):
            self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
            writer.gen_catch_invalid_argument(error_val='-1')


class ObjObjProcGen(FuncBase):
    """objobjproc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body, *,
                 arg2name=None):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, None, body)
        if arg2name is None:
            arg2name = 'obj2'
        self.__args = [CArg.Self(),
                       CArg.PyArg(arg2name)]

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='int',
                                   func_name=self.name,
                                   args=self.__args):
            self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
            writer.gen_catch_invalid_argument(error_val='-1')


class ObjObjArgProcGen(FuncBase):
    """objobjargproc 型の関数を生成するクラス
    """

    def __init__(self, gen, name, body, *,
                 arg2name=None,
                 arg3name=None):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, None, body)
        if arg2name is None:
            arg2name = 'obj2'
        if arg3name is None:
            arg3name = 'obj3'
        self.__args = [CArg.Self(),
                       CArg.PyArg(arg2name),
                       CArg.PyArg(arg3name)]

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='int',
                                   func_name=self.name,
                                   args=self.__args):
            self.gen.gen_ref_conv(writer, refname='val')
            with writer.gen_try_block():
                self.body(writer)
            writer.gen_catch_invalid_argument(error_val='-1')


class ConvGen:
    """Conv ファンクタクラスを生成するクラス
    """

    def __init__(self, gen, body):
        self.gen = gen
        if body == 'default':
            # デフォルト実装
            def default_body(writer):
                gen.gen_alloc_code(writer, varname='obj')
                gen.gen_obj_conv(writer, objname='obj', varname='my_obj')
                writer.write_line(f'new (&my_obj->mVal) {gen.classname}(val);')
                writer.gen_return('obj')
            body = default_body
        self.body = body
        self.args = [CArg.GenArg('const ElemType&', 'val',
                                 comment='[in] 元の値')]

    def gen_decl(self, writer):
        """ヘッダ用の宣言を生成する．
        """
        with writer.gen_struct_block('Conv',
                                     dox_comment=f'@brief {self.gen.classname} を PyObject* に変換するファンクタクラス'):
            writer.gen_func_declaration(no_crlf=True,
                                        return_type='PyObject*',
                                        func_name='operator()',
                                        args=self.args)

    def gen_tofunc(self, writer):
        """ToPyObject() 関数の定義を生成する．
        """
        dox_comments = [f'@brief {self.gen.classname} を表す PyObject を作る．',
                        '@return 生成した PyObject を返す．',
                        '',
                        '返り値は新しい参照が返される．']
        with writer.gen_func_block(dox_comments=dox_comments,
                                   is_static=True,
                                   return_type='PyObject*',
                                   func_name='ToPyObject',
                                   args=self.args):
            writer.gen_vardecl(typename='Conv',
                               varname='conv')
            writer.gen_return('conv(val)')

    def __call__(self, writer):
        with writer.gen_func_block(comment=f'{self.gen.classname} を PyObject に変換する．',
                                   return_type='PyObject*',
                                   func_name=f'{self.gen.pyclassname}::Conv::operator()',
                                   args=self.args):
            self.body(writer)


class DeconvGen:
    """Deconv ファンクタクラスを生成するクラス
    """

    def __init__(self, gen, body, *,
                 extra_func=None,
                 error_value=None):
        self.gen = gen
        if body == 'default':
            # デフォルト実装
            def default_body(writer):
                gen.gen_raw_conv(writer)
                writer.gen_return('false')
            body = default_body
        self.body = body
        self.args = [CArg.PyArg('obj',
                                comment='[in] Python のオブジェクト'),
                     CArg.GenArg('ElemType&', 'val',
                                 comment='[out] 結果を格納する変数')]
        self.error_value = error_value
        self.__extra_func = extra_func

    def gen_decl(self, writer):
        """ヘッダ用の宣言を生成する．
        """
        with writer.gen_struct_block('Deconv',
                                     dox_comment=f'@brief PyObject* から {self.gen.classname} を取り出すファンクタクラス'):
            writer.gen_func_declaration(no_crlf=True,
                                        return_type='bool',
                                        func_name='operator()',
                                        args=self.args)

    def gen_fromfunc(self, writer):
        """FromPyObject() 関数の定義を生成する．
        """
        dox_comments = [f'@brief PyObject から {self.gen.classname} を取り出す．',
                        '@return 正しく変換できた時に true を返す．']
        with writer.gen_func_block(dox_comments=dox_comments,
                                   is_static=True,
                                   return_type='bool',
                                   func_name='FromPyObject',
                                   args=self.args):
            writer.gen_vardecl(typename='Deconv',
                               varname='deconv')
            writer.gen_return('deconv(obj, val)')

    def __call__(self, writer):
        with writer.gen_func_block(comment=f'PyObject を {self.gen.classname} に変換する．',
                                   return_type='bool',
                                   func_name=f'{self.gen.pyclassname}::Deconv::operator()',
                                   args=self.args):
            if self.__extra_func is not None:
                with writer.gen_if_block(f'{self.__extra_func}(obj, val)'):
                    writer.gen_return('true')
            self.body(writer)

