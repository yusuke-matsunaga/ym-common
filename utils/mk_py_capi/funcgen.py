#! /usr/bin/env python3

""" 関数定義を生成するクラス定義ファイル

:file: funcgen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""


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
    
    def __init__(self, gen, name, body):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        elif body == 'default':
            # デフォルト実装
            def default_body(writer):
                writer.write_line(f'obj->mVal.~{gen.classname}()')
            body = default_body
        self = super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
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
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
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
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='Py_hash_t',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)


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
        super().__init__(gen, name, body, arg_list)
        self.__args = ('PyObject* self',
                       f'PyObject* {arg2name}',
                       f'PyObject* {arg3name}')

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
            self.body(writer)


class RichcmpFuncGen(FuncBase):
    """richcmpfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        if body is None:
            # 空
            def null_body(writer):
                writer.gen_comments(['self と other を比較して結果のブール値を表す PyObject* を返す．',
                                     'op の値は Py_LT, Py_LE, Py_EQ, Py_NE, Py_GT, Py_GE のいずれか．',
                                     'サポートしていない演算の場合は Py_RETURN_NOTIMPLEMETED を返す．'])
            body = null_body
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = ('PyObject* self',
                'PyObject* other',
                'int op')
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.body(writer)


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
        super().__init__(gen, name, body, arg_list)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = ('PyObject* self',
                'PyObject* args',
                'PyObject* kwds')
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            writer.gen_func_preamble(self.arg_list)
            self.body(writer)


class NewFuncGen(FuncWithArgs):
    """newfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body, arg_list):
        if body is None:
            # 空
            def null_body(writer):
                writer.gen_comment('内容をセットした PyObject* を生成し，返す．')
            body = null_body
        elif body == 'sample':
            # sample 実装
            def sample_body(writer):
                writer.gen_comment('この関数は実際には機能しない．')
                writer.gen_auto_assign('self', 'type->tp_alloc(type, 0)')
                gen.gen_obj_conv(writer, varname='my_obj')
                writer.write_line(f'new (&myobj->mVal) {gen.classname}()')
                writer.gen_return('self')
            body = sample_body
        super().__init__(gen, name, body, arg_list)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = ('PyTypeObject* type',
                'PyObject* args',
                'PyObject* kwds')
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            writer.gen_func_preamble(self.arg_list)
            self.body(writer)


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
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='Py_ssize_t',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)
            writer.gen_return('len_val')
            

class InquiryGen(FuncBase):
    """inquiry 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='int',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)
            writer.gen_return('inquiry_val')

            
class UnaryFuncGen(FuncBase):
    """unaryfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = ('PyObject* self', )
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)


class BinaryFuncGen(FuncBase):
    """binaryfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body, *,
                 arg2name='other'):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, body)
        self.__args = ('PyObject* self',
                       f'PyObject* {arg2name}')

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=self.__args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)


class TernaryFuncGen(FuncBase):
    """ternaryfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body, *,
                 arg2name='obj2',
                 arg3name='obj3'):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, body)
        self.__args = ('PyObject* self',
                       f'PyObject* {arg2name}',
                       f'PyObject* {arg3name}')

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=self.__args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)


class SsizeArgFuncGen(FuncBase):
    """ssizeargfunc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body, *,
                 arg2name='arg2'):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, body)
        self.__args = ('PyObject* self',
                       f'Py_ssize_t {arg2name}')

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=self.__args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)


class SsizeObjArgProcGen(FuncBase):
    """ssizeobjargproc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body, *,
                 arg2name='arg2',
                 arg3name='arg3'):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, body)
        self.__args = ('PyObject* self',
                       f'Py_ssize_t {arg2name}',
                       f'PyObject* {arg3name}')

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='int',
                                   func_name=self.name,
                                   args=self.__args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)


class ObjObjProcGen(FuncBase):
    """objobjproc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body, *,
                 arg2name='obj2'):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, body)
        self.__args = ('PyObject* self',
                       f'PyObject* {arg2name}')

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='int',
                                   func_name=self.name,
                                   args=self.__args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)


class ObjObjArgProcGen(FuncBase):
    """objobjargproc 型の関数を生成するクラス
    """
    
    def __init__(self, gen, name, body, *,
                 arg2name='obj2',
                 arg3name='obj3'):
        if body is None:
            # 空
            def null_body(writer):
                pass
            body = null_body
        super().__init__(gen, name, body)
        self.__args = ('PyObject* self',
                       f'PyObject* {arg2name}',
                       f'PyObject* {arg3name}')

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='int',
                                   func_name=self.name,
                                   args=self.__args):
            self.gen.gen_ref_conv(writer, refname='val')
            self.body(writer)


class ConvGen:
    """Conv ファンクタクラスを生成するクラス
    """

    def __init__(self, gen, body):
        self.gen = gen
        if body == 'default':
            # デフォルト実装
            def default_body(writer):
                writer.write_line(f'new (&my_obj->mVal) {gen.classname}(val);')
            body = default_body
        self.body = body

    def gen_decl(self, writer):
        """ヘッダ用の宣言を生成する．
        """
        with writer.gen_struct_block('Conv',
                                     dox_comment=f'@brief {self.gen.classname} を PyObject* に変換するファンクタクラス'):
            writer.gen_func_declaration(no_crlf=True,
                                        return_type='PyObject*',
                                        func_name='operator()',
                                        args=('const ElemType& val', ))

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
                                   args=('const ElemType& val ///< [in] 値', )):
            writer.gen_vardecl(typename='Conv',
                               varname='conv')
            writer.gen_return('conv(val)')
        
    def __call__(self, writer):
        with writer.gen_func_block(comment=f'{self.gen.classname} を PyObject に変換する．',
                                   return_type='PyObject*',
                                   func_name=f'{self.gen.pyclassname}::Conv::operator()',
                                   args=(f'const {self.gen.classname}& val', )):
            writer.gen_auto_assign('type', f'{self.gen.pyclassname}::_typeobject()')
            writer.gen_auto_assign('obj', 'type->tp_alloc(type, 0)')
            writer.gen_auto_assign('my_obj', f'reinterpret_cast<{self.gen.objectname}*>(obj)')
            self.body(writer)
            writer.gen_return('obj')


class DeconvGen:
    """Deconv ファンクタクラスを生成するクラス
    """

    def __init__(self, gen, body):
        self.gen = gen
        if body == 'default':
            # デフォルト実装
            def default_body(writer):
                with writer.gen_if_block(f'{gen.pyclassname}::Check(obj)'):
                    writer.gen_assign('val', f'{gen.pyclassname}::_get_ref(obj)')
                    writer.gen_return('true')
                writer.gen_return('false')
            body = default_body
        self.body = body

    def gen_decl(self, writer):
        """ヘッダ用の宣言を生成する．
        """
        with writer.gen_struct_block('Deconv',
                                     dox_comment=f'@brief PyObject* から {self.gen.classname} を取り出すファンクタクラス'):
            args = ('PyObject* obj',
                    'ElemType& val')
            writer.gen_func_declaration(no_crlf=True,
                                        return_type='bool',
                                        func_name='operator()',
                                        args=args)

    def gen_fromfunc(self, writer):
        """FromPyObject() 関数の定義を生成する．
        """
        dox_comments = [f'@brief PyObject から {self.gen.classname} を取り出す．',
                        '@return 正しく変換できた時に true を返す．']
        with writer.gen_func_block(dox_comments=dox_comments,
                                   is_static=True,
                                   return_type='bool',
                                   func_name='FromPyObject',
                                   args=('PyObject* obj, ///< [in] Python のオブジェクト',
                                         'ElemType& val  ///< [out] 結果を格納する変数')):
            writer.gen_vardecl(typename='Deconv',
                               varname='deconv')
            writer.gen_return('deconv(obj, val)')
        
    def __call__(self, writer):
        args = ('PyObject* obj',
                f'{self.gen.classname}& val')
        with writer.gen_func_block(comment=f'PyObject を {self.gen.classname} に変換する．',
                                   return_type='bool',
                                   func_name=f'{self.gen.pyclassname}::Deconv::operator()',
                                   args=args):
            self.body(writer)
        
