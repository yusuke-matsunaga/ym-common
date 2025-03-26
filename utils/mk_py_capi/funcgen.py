#! /usr/bin/env python3

""" FuncGen の定義ファイル

:file: funcgen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi.codegenbase import CodeGenBase


class FuncBase(CodeGenBase):
    """関数を生成する基底クラス

    主に引数に関する処理を実装している．
    """

    def __init__(self, parent, *,
                 arg_list=[],
                 doc_str=None):
        super().__init__(parent)
        self.arg_list = arg_list
        if len(arg_list) == 0:
            self.has_args = False
            self.has_keywords = False
        else:
            self.has_args = True
            for arg in arg_list:
                if arg.name is not None:
                    self.has_keywords = True
        self.doc_str = doc_str

    def gen_preamble(self):
        """引数を解釈する前処理のコードを生成する．
        """
        if self.has_keywords:
            # キーワードテーブルの定義
            kwds_table = 'kwlist'
            with self.gen_array_block(typename='static const char*',
                                      arrayname=kwds_table):
                for arg in self.arg_list:
                    if arg.name is None:
                        self._write_line('"",')
                    else:
                        self._write_line(f'"{arg.name}",')
                self._write_line('nullptr')

        # パーズ結果を格納する変数の宣言
        for arg in self.arg_list:
            arg.gen_vardef()

        # PyArg_Parse() 用のフォーマット文字列の生成
        fmt_str = ""
        mode = "init" # init|option|keyword の3つ
        for arg in self.arg_list:
            if arg.option:
                if mode == "init":
                    fmt_str += "|"
                    mode = "option"
            if arg.name is None:
                if mode == "keyword":
                    raise ValueError('nameless argument is not allowed here')
            else:
                if mode == "option":
                    fmt_str += "$"
                    mode = "keyword"
            fmt_str += f'{arg.pchar}'
                    
        # パーズ関数の呼び出し
        if self.has_args:
            if self.has_keywords:
                line = f'if ( !PyArg_ParseTupleAndKeywords(args, kwds, "{fmt_str}",'
                self._write_line(line)
                fpos = line.find('(')
                delta = line.find('(', fpos + 1) + 1
                self._indent_inc(delta)
                self._write_line(f'const_cast<char**>({kwds_table}),')
            else:
                line = f'if ( !PyArg_Parse(args, "{fmt_str}",'
                fpos = line.find('(')
                delta = line.find('(', fpos + 1) + 1
            nargs = len(self.arg_list)
            for i, arg in enumerate(self.arg_list):
                line = arg.gen_varref()
                if i < nargs - 1:
                    line += ','
                else:
                    line += ') ) {'
                self._write_line(line)
            self._indent_dec(delta)
            self._indent_inc()
            self.gen_return('nullptr')
            self._indent_dec()
            self._write_line('}')

        # PyObject から C++ の変数へ変換する．
        for arg in self.arg_list:
            arg.gen_conv()

    def gen_obj_conv(self, varname):
        """self から自分の型に変換するコードを生成する．
        """
        self.gen_auto_assign(f'{varname}',
                             f'reinterpret_cast<{self.objectname}*>(self)')

    def gen_val_conv(self, varname):
        """self から値を取り出すコードを生成する．
        """
        self.gen_assign(f'auto& {varname}',
                        f'{self.pyclassname}::_get_ref(self)')

    
class MethodGen(FuncBase):
    """メソッドを実装するためのC++コードを生成するクラス
    """

    def __init__(self, parent, *,
                 name,
                 func_name,
                 arg_list,
                 is_static=False,
                 doc_str):
        super().__init__(parent,
                         arg_list=arg_list,
                         doc_str=doc_str)
        self.name = name
        self.func_name = func_name
        self.is_static = is_static
        parent.add_method(self)
    
    def __call__(self, func_name):
        if self.is_static:
            args0 = 'PyObject* Py_UNUSED(self)'
        else:
            args0 = 'PyObject* self'
        if self.has_args:
            arg1 = 'PyObject* args'
        else:
            arg1 = 'PyObject* Py_UNUSED(args)'
        if self.has_keywords:
            arg2 = 'PyObject* kwds'
            args = [ args0, arg1, arg2 ]
        else:
            args = [ args0, arg1 ]
        with self.gen_func_block(description=self.doc_str,
                                 return_type='PyObject*',
                                 func_name=func_name,
                                 args=args):
            self.gen_preamble()
            self.gen_body()

    def gen_body(self):
        pass


class NewGen(FuncBase):
    """new 関数を生成するクラス
    """

    def __init__(self, parent, *,
                 arg_list):
        super().__init__(parent,
                         arg_list=arg_list)
        parent.new_gen = self
        
    def __call__(self, func_name):
        args = ('PyTypeObject* type',
                'PyObject* args',
                'PyObject* kwds')
        with self.gen_func_block(return_type='PyObject*',
                                 func_name=func_name,
                                 args=args):
            self.gen_preamble()
            self.gen_body()


class DeallocGen(FuncBase):
    """dealloc 関数を生成するクラス

    必要に応じて継承クラスを作り gen_body() をオーバーロードすること
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        parent.dealloc_gen = self

    def __call__(self, func_name):
        with self.gen_func_block(description='終了関数',
                                 return_type='void',
                                 func_name=func_name,
                                 args=(('PyObject* self', ))):
            self.gen_obj_conv('obj')
            self.gen_body()
            self._write_line('PyTYPE(self)->tp_free(self)')

    def gen_body(self):
        self._write_line(f'obj->mVal.~{self.classname}()')


class ReprGen(FuncBase):
    """repr 関数を生成するクラス

    必ず継承クラスを作り gen_body() をオーバーロードすること
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        parent.repr_gen = self

    def __call__(self, func_name):
        with self.gen_func_block(description='repr関数',
                                 return_type='PyObject*',
                                 func_name=func_name,
                                 args=(('PyObject* self', ))):
            self.gen_val_conv('val')
            self.gen_body('val', 'repr_str')
            self._write_line(f'return PyString::ToPyObject(repr_str);')

    def gen_body(self, varname, strname):
        """C++ 上の変数 varname の内容を表す文字列を作るコードを生成する．
        """
        raise TypeError('gen_body() is not implemented')


class ConvGen(CodeGenBase):
    """PyObject* に変換するファンクタクラスのコードを出力する．

    対象のクラスがコピーコンストラクタを実装しているかぎり
    このデフォルト実装で正しく動くはず．
    カスタマイズする場合には gen_body() をオーバーロードすればよい．
    gen_body() では obj1->mVal を val の値で初期化するコードを
    出力する．
    """
    def __init__(self, parent):
        super().__init__(parent)
        parent.conv_gen = self
        
    def __call__(self):
        description = f'{self.classname} を PyObject に変換する．'
        with self.gen_func_block(description=description,
                                 return_type='PyObject*',
                                 func_name=f'{self.pyclassname}::Conv::operator()',
                                 args=(f'const {self.classname}& val', )):
            self.gen_auto_assign('type', f'{self.pyclassname}::_typeobject()')
            self.gen_auto_assign('obj', 'type->tp_alloc(type, 0)')
            self.gen_auto_assign('obj1', f'reinterpret_cast<{self.objectname}*>(obj)')
            self.gen_body()
            self.gen_return('obj')

    def gen_body(self):
        self._write_line(f'new (&obj1->mVal) {self.classname}(val);')


class DeconvGen(CodeGenBase):
    """PyObject* から変換するファンクタクラスのコードを出力する．

    デフォルトの実装では PyClass::mVal の値を取り出しているが，
    他の型からの変換を行う場合には gen_body() をオーバーロードする必要がある．
    gen_body() は PyObject* obj から val に値の変換を試みて成功したら
    true を返す．
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        parent.deconv_gen = self

    def __call__(self):
        description = f'PyObject を {self.classname} に変換する．'
        with self.gen_func_block(description=description,
                                 return_type='bool',
                                 func_name=f'{self.pyclassname}::Deconv::operator()',
                                 args=('PyObject* obj',
                                       f'{self.classname}& val')):
            self.gen_body()

    def gen_body(self):
        with self.gen_if_block(f'{self.pyclassname}::Check(obj)'):
            self.gen_assign('val', f'{self.pyclassname}::_get_ref(obj)')
            self.gen_return('true')
        self.gen_return('false')


class PreambleGen(CodeGenBase):
    """共通な定数の定義などを行う．
    """

    def __init__(self, parent):
        super().__init__(parent)
        parent.preamble_gen = self

    def __call__(self):
        pass
