#! /usr/bin/env python3

""" PyObjGen のクラス定義ファイル

:file: pyobj_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

import re
import os
import datetime
import sys
from .funcgen import DeallocGen
from .funcgen import ReprFuncGen
from .funcgen import HashFuncGen
from .funcgen import RichcmpFuncGen
from .funcgen import InitProcGen
from .funcgen import NewFuncGen
from .funcgen import LenFuncGen
from .funcgen import InquiryGen
from .funcgen import UnaryFuncGen
from .funcgen import BinaryFuncGen
from .funcgen import TernaryFuncGen
from .funcgen import SsizeArgFuncGen
from .funcgen import SsizeObjArgProcGen
from .funcgen import ObjObjProcGen
from .funcgen import ObjObjArgProcGen
from .number_gen import NumberGen
from .sequence_gen import SequenceGen
from .mapping_gen import MappingGen
from .method_gen import MethodGen
from .getset_gen import GetSetGen
from .utils import gen_func
from .cxxwriter import CxxWriter


class PyObjGen:
    """PyObject の拡張クラスを生成するクラス
    """
    
    def __init__(self, *,
                 classname,
                 pyclassname=None,
                 namespace=None,
                 typename=None,
                 objectname=None,
                 pyname,
                 header_include_files=[],
                 source_include_files=[]):
        # C++ のクラス名
        self.classname = classname
        # Python-CAPI 用のクラス名
        if pyclassname is None:
            self.pyclassname = f'Py{classname}'
        # 名前空間
        self.namespace = namespace
        # Python-CAPI 用のタイプクラス名
        if typename is None:
            self.typename = f'{classname}_Type'
        # Python-CAPI 用のオブジェクトクラス名
        if objectname is None:
            self.objectname = f'{classname}_Object'
        # Python のクラス名
        self.pyname = pyname
        
        # ヘッダファイル用のインクルードファイルリスト
        self.header_include_files = header_include_files
        # ソースファイル用のインクルードファイルリスト
        self.source_include_files = source_include_files

        # 出力するC++の変数名の重複チェック用の辞書
        self.__name_dict = set()

        # プリアンブル出力器
        self.__preamble_gen = None

        # 組み込み関数生成器
        self.__dealloc_gen = None
        self.__repr_gen = None
        self.__hash_gen = None
        self.__call_gen = None
        self.__str_gen = None
        self.__richcompare_gen = None
        self.__init_gen = None
        self.__new_gen = None

        # Number 構造体の定義
        self.__number_name = None
        self.__number_gen = None

        # Sequence 構造体の定義
        self.__sequence_name = None
        self.__sequence_gen = None

        # Mapping 構造体の定義
        self.__mapping_name = None
        self.__mapping_gen = None

        # メソッド構造体の定義
        self.__method_name = self.__check_name('method')
        self.__method_gen = MethodGen()

        # get/set 構造体の定義
        self.__getset_name = self.__check_name('getset')
        self.__getset_gen = GetSetGen()

        # 追加の初期化コード
        self.__ex_init_gen = None

        # PyObject への変換を行うコード
        self.__conv_gen = None

        # PyObject からの逆変換を行うコード
        self.__deconv_gen = None

        self.basicsize = f'sizeof({self.objectname})'
        self.itemsize = '0'
        self.flags = 'Py_TPFLAGS_DEFAULT'
        
        # 説明文
        self.doc_str = f'{self.classname} object'

        # 置換用のパタン
        # 字下げ位置を求めるために正規表現を用いている．
        self.__conv_def_pat = re.compile('^(\s*)%%CONV_DEF%%$')
        self.__deconv_def_pat = re.compile('^(\s*)%%DECONV_DEF%%$')
        self.__to_def_pat = re.compile('^(\s*)%%TOPYOBJECT%%$')
        self.__from_def_pat = re.compile('^(\s*)%%FROMPYOBJECT%%$')
        self.__tp_init_pat = re.compile('^(\s*)%%TP_INIT_CODE%%$')
        self.__ex_init_pat = re.compile('^(\s*)%%EX_INIT_CODE%%$')

    def add_preamble(self, func_body):
        if self.__preamble_gen is not None:
            raise ValueError("preamble has benn already defined")
        self.__preamble_gen = func_body
        
    def add_dealloc(self, *,
                    func_name=None,
                    dealloc_func=None):
        """dealloc 関数定義を追加する．
        """
        if self.__dealloc_gen is not None:
            raise ValueError('dealloc has been already defined')
        func_name = self.__complete(func_name, 'dealloc_func')
        self.__dealloc_gen = DeallocGen(self, func_name, dealloc_func)

    def add_repr(self, *,
                 func_name=None,
                 repr_func=None):
        """repr 関数定義を追加する．
        """
        if self.__repr_gen is not None:
            raise ValueError('repr has been already defined')
        func_name = self.__complete(func_name, 'repr_func')
        self.__repr_gen = ReprFuncGen(self, func_name, repr_func)

    def add_hash(self, *,
                 func_name=None,
                 hash_func=None):
        """hash 関数定義を追加する．
        """
        if self.__hash_gen is not None:
            raise ValueError('hash has been already defined')
        func_name = self.__complete(func_name, 'hash_func')
        self.__hash_gen = HashFuncGen(self, func_name, hash_func)

    def add_call(self, *,
                 func_name=None,
                 call_func=None):
        """call 関数定義を追加する．
        """
        if self.__call_gen is not None:
            raise ValueError('hash has been already defined')
        func_name = self.__complete(func_name, 'call_func')
        self.__call_gen = TernaryFuncGen(self, func_name, call_func)

    def add_str(self, *,
                func_name=None,
                str_func=None):
        """str 関数定義を追加する．
        """
        if self.__str_gen is not None:
            raise ValueError('str has been already defined')
        func_name = self.__complete(func_name, 'str_func')
        self.__str_gen = ReprFuncGen(self, func_name, str_func)

    def add_richcompare(self, *,
                        func_name=None,
                        cmp_func=None):
        """richcompare 関数定義を追加する．
        """
        if self.__richcompare_gen is not None:
            raise ValueError('richcompare has been already defined')
        func_name = self.__complete(func_name, 'richcompare_func')
        self.__richcompare_gen = RichcmpFuncGen(self, func_name, cmp_func)
        
    def add_number(self, *,
                   name=None,
                   nb_add=None,
                   nb_subtract=None,
                   nb_multiply=None,
                   nb_remainder=None,
                   nb_divmod=None,
                   nb_power=None,
                   nb_negative=None,
                   nb_positive=None,
                   nb_absolute=None,
                   nb_bool=None,
                   nb_invert=None,
                   nb_lshift=None,
                   nb_rshift=None,
                   nb_and=None,
                   nb_xor=None,
                   nb_or=None,
                   nb_int=None,
                   nb_float=None,
                   nb_inplace_add=None,
                   nb_inplace_subtract=None,
                   nb_inplace_multiply=None,
                   nb_inplace_remainder=None,
                   nb_inplace_power=None,
                   nb_inplace_lshift=None,
                   nb_inplace_rshift=None,
                   nb_inplace_and=None,
                   nb_inplace_xor=None,
                   nb_inplace_or=None,
                   nb_floor_divide=None,
                   nb_true_divide=None,
                   nb_inplace_floor_divide=None,
                   nb_inplace_true_divide=None,
                   nb_index=None,
                   nb_matrix_multiply=None,
                   nb_inplace_matrix_multiply=None):
        """Number オブジェクト構造体を定義する．
        """
        if self.__number_gen is not None:
            raise ValueError('number has been already defined')
        self.__number_name = self.__complete(name, 'number')
        self.__number_gen = NumberGen(
            self,
            nb_add=nb_add,
            nb_subtract=nb_subtract,
            nb_multiply=nb_multiply,
            nb_remainder=nb_remainder, 
            nb_divmod=nb_divmod,
            nb_power=nb_power,
            nb_negative=nb_negative,
            nb_positive=nb_positive,
            nb_absolute=nb_absolute,
            nb_bool=nb_bool,
            nb_invert=nb_invert, 
            nb_lshift=nb_lshift, 
            nb_rshift=nb_rshift, 
            nb_and=nb_and,
            nb_xor=nb_xor,
            nb_or=nb_or,
            nb_int=nb_int,
            nb_float=nb_float,
            nb_inplace_add=nb_inplace_add,
            nb_inplace_subtract=nb_subtract,
            nb_inplace_multiply=nb_inplace_multiply,
            nb_inplace_remainder=nb_inplace_remainder,
            nb_inplace_power=nb_inplace_power,
            nb_inplace_lshift=nb_inplace_lshift,
            nb_inplace_rshift=nb_inplace_rshift,
            nb_inplace_and=nb_inplace_and,
            nb_inplace_xor=nb_inplace_xor,
            nb_inplace_or=nb_inplace_or,
            nb_floor_divide=nb_floor_divide,
            nb_true_divide=nb_true_divide,
            nb_inplace_floor_divide=nb_inplace_floor_divide,
            nb_inplace_true_divide=nb_inplace_true_divide,
            nb_index=nb_index,
            nb_matrix_multiply=nb_matrix_multiply,
            nb_inplace_matrix_multiply=nb_inplace_matrix_multiply)
        
    def add_sequence(self, *,
                     name=None,
                     sq_length=None,
                     sq_concat=None,
                     sq_repeat=None,
                     sq_item=None,
                     sq_ass_item=None,
                     sq_contains=None,
                     sq_inplace_concat=None,
                     sq_inplace_repeat=None):
        """Sequence オブジェクト構造体を定義する．
        """
        if self.__sequence_gen is not None:
            raise ValueError('sequence has been already defined')
        self.__sequence_name = self.__complete(name, 'sequence')
        self.__sequence_gen = SequenceGen(
            self,
            sq_length=sq_length,
            sq_concat=sq_concat,
            sq_repeat=sq_repeat,
            sq_item=sq_item,
            sq_ass_item=sq_ass_item,
            sq_contains=sq_contains,
            sq_inplace_concat=sq_inplace_concat,
            sq_inplace_repeat=sq_inplace_repeat)

    def add_mapping(self, *,
                    name=None,
                    mp_length=None,
                    mp_subscript=None,
                    mp_ass_subscript=None):
        """Mapping オブジェクト構造体を定義する．
        """
        if self.__mapping_gen is not None:
            raise ValueError('mapping has been already defined')
        self.__mapping_name = self.__complete(name, 'mapping')
        self.__mapping_gen = MappingGen(
            self,
            mp_length=mp_length,
            mp_subscript=mp_subscript,
            mp_ass_subscript=mp_ass_subscript)
        
    def add_init(self, *,
                 func_name=None,
                 func_body=None,
                 arg_list=[]):
        """init 関数定義を追加する．
        """
        if self.__init_gen is not None:
            raise ValueError('init has been already defined')
        func_name = self.__complete(func_name, 'init_func')
        self.__init_gen = InitProcGen(self, func_name, func_body, arg_list)
        
    def add_new(self, *,
                func_name=None,
                func_body=None,
                arg_list=[]):
        """new 関数定義を追加する．
        """
        if self.__new_gen is not None:
            raise ValueError('new has been already defined')
        func_name = self.__complete(func_name, 'new_func')
        self.__new_gen = NewFuncGen(self, func_name, func_body, arg_list)
        
    def add_method(self, name, *,
                   func_name=None,
                   arg_list=[],
                   is_static=False,
                   func_body=None,
                   doc_str=''):
        """メソッド定義を追加する．
        """
        # デフォルトの関数名は Python のメソッド名をそのまま用いる．
        func_name = self.__complete(func_name, name)
        self.__method_gen.add(self, func_name,
                              name=name,
                              arg_list=arg_list,
                              is_static=is_static,
                              func_body=func_body,
                              doc_str=doc_str)

    def add_getter(self, func_name, *,
                   has_closure=False,
                   func_body=None):
        """getter 定義を追加する．
        """
        self.__check_name(func_name)
        self.__getset_gen.add_getter(self, func_name,
                                     has_closure=has_closure,
                                     func_body=func_body)

    def add_setter(self, func_name, *,
                   has_closure=False,
                   func_body=None):
        """setter 定義を追加する．
        """
        self.__check_name(func_name)
        self.__getset_gen.add_setter(self, func_name,
                                     has_closure=has_closure,
                                     func_body=func_body)

    def add_attr(self, name, *,
                 getter_name=None,
                 setter_name=None,
                 closure=None,
                 doc_str=''):
        """属性定義を追加する．
        """
        self.__getset_gen.add_attr(name,
                                   getter_name=getter_name,
                                   setter_name=setter_name,
                                   closure=closure,
                                   doc_str=doc_str)

    def new_lenfunc(self, name, body):
        return LenFuncGen(self, name, body)

    def new_inquiry(self, name, body):
        return InquiryGen(self, name, body)

    def new_unaryfunc(self, name, body):
        return UnaryFuncGen(self, name, body)

    def new_binaryfunc(self, name, body):
        return BinaryFuncGen(self, name, body)

    def new_ternaryfunc(self, name, body):
        return TernaryFuncGen(self, name, body)

    def new_ssizeargfunc(self, name, body):
        return SsizeArgFuncGen(self, name, body)

    def new_ssizeobjargproc(self, name, body):
        return SsizeObjArgProcGen(self, name, body)

    def new_objobjproc(self, name, body):
        return ObjObjProcGen(self, name, body)

    def new_objobjargproc(self, name, body):
        return ObjObjArgProcGen(self, name, body)
    
    def add_conv(self, func_body=None):
        if func_body is None:
            # デフォルト実装
            def conv_gen(writer):
                writer.write_line(f'new (&obj1->mVal) {self.classname}(val);')
            func_body = conv_gen
        self.__conv_gen = func_body

    def add_deconv(self, func_body=None):
        if func_body is None:
            # デフォルト実装
            def deconv_gen(writer):
                with writer.gen_if_block(f'{gen.pyclassname}::Check(obj)'):
                    writer.gen_assign('val', f'{gen.pyclassname}::_get_ref(obj)')
                    writer.gen_return('true')
                writer.gen_return('false')
            func_body = deconv_gen
        self.__deconv_gen = func_body
                
    def make_header(self, fout=sys.stdout):
        """ヘッダファイルを出力する．"""

        # テンプレートファイルは同じディレクトリにあると仮定している．
        template_file = self.template_file("PyCustom.h")

        # 結果のヘッダファイル名
        header_file = f'{self.pyclassname}.h'

        # インタロック用マクロ名
        cap_header_file = self.pyclassname.upper()

        writer = CxxWriter(fout=fout)
        with open(template_file, 'rt') as fin:
            for line in fin:
                # 余分な改行を削除
                line = line.rstrip()

                if line == '%%INCLUDES%%':
                    # インクルードファイルの置換
                    for filename in self.header_include_files:
                        writer.gen_include(filename)
                    continue

                if line == '%%BEGIN_NAMESPACE%%':
                    # 名前空間の開始
                    if self.namespace is not None:
                        writer.write_line(f'BEGIN_NAMESPACE_{self.namespace}')
                    continue

                if line == '%%END_NAMESPACE%%':
                    # 名前空間の終了
                    if self.namespace is not None:
                        writer.write_line(f'END_NAMESPACE_{self.namespace}')
                    continue
                
                result = self.__conv_def_pat.match(line)
                if result:
                    # Conv の宣言
                    writer.indent_set(len(result.group(1)))
                    self.conv_def_gen(writer)
                    writer.indent_set(0)
                    continue

                result = self.__deconv_def_pat.match(line)
                if result:
                    # Deconv の宣言
                    writer.indent_set(len(result.group(1)))
                    self.deconv_def_gen(writer)
                    writer.indent_set(0)
                    continue

                result = self.__to_def_pat.match(line)
                if result:
                    # ToPyObject の宣言
                    writer.indent_set(len(result.group(1)))
                    self.to_def_gen(writer)
                    writer.indent_set(0)
                    continue

                result = self.__from_def_pat.match(line)
                if result:
                    # FromPyObject の宣言
                    writer.indent_set(len(result.group(1)))
                    self.from_def_gen(writer)
                    writer.indent_set(0)
                    continue
                
                # 年の置換
                line = line.replace('%%Year%%', self.year())
                # インタロック用マクロ名の置換
                line = line.replace('%%PYCUSTOM%%', cap_header_file)
                # クラス名の置換
                line = line.replace('%%Custom%%', self.classname)
                # Python 拡張用のクラス名の置換
                line = line.replace('%%PyCustom%%', self.pyclassname)
                # 名前空間の置換
                if self.namespace is not None:
                    line = line.replace('%%NAMESPACE%%', self.namespace)

                writer.write_line(line)

    def conv_def_gen(self, writer):
        writer.gen_CRLF()
        if self.__conv_gen is None:
            if self.__deconv_gen is None:
                writer.gen_comment('このクラスは Conv/Deconv を持たない．')
            else:
                writer.gen_comment('このクラスは Conv を持たない．')
        else:
            writer.gen_dox_comment(f'@brief {self.classname} を PyObject* に変換するファンクタクラス')
            with writer.gen_struct_block('Conv'):
                args = ('const ElemType& val', )
                writer.gen_func_declaration(return_type='PyObject*',
                                            func_name='operator()',
                                            args=args)

    def deconv_def_gen(self, writer):
        if self.__deconv_gen is None:
            if self.__conv_gen is not None:
                writer.gen_CRLF()
                writer.gen_comment('このクラスは Deconv を持たない．')
        else:
            writer.gen_CRLF()
            writer.gen_dox_comment(f'@brief PyObject* から {self.classname} を取り出すファンクタクラス')
            with writer.gen_struct_block('Deconv'):
                args = ('PyObject* obj',
                        'ElemType& val')
                writer.gen_func_declaration(return_type='bool',
                                            func_name='operator()',
                                            args=args)
                
    def to_def_gen(self, writer):
        if self.__conv_gen is not None:
            writer.gen_CRLF()
            writer.gen_dox_comment(f'@brief {self.classname} を表す PyObject を作る．')
            writer.gen_dox_comment('@return 生成した PyObject を返す．')
            writer.gen_dox_comment('')
            writer.gen_dox_comment('返り値は新しい参照が返される．')
            with writer.gen_func_block(is_static=True,
                                       return_type='PyObject*',
                                       func_name='ToPyObject',
                                       args=('const ElemType& val ///< [in] 値', )):
                writer.gen_vardecl(typename='Conv',
                                   varname='conv')
                writer.gen_return('conv(val)')

    def from_def_gen(self, writer):
        if self.__deconv_gen is not None:
            writer.gen_CRLF()
            writer.gen_dox_comment(f'@brief PyObject から {self.classname} を取り出す．')
            writer.gen_dox_comment('@return 正しく変換できた時に true を返す．')
            with writer.gen_func_block(is_static=True,
                                       return_type='bool',
                                       func_name='FromPyObject',
                                       args=('PyObject* obj, ///< [in] Python のオブジェクト',
                                             'ElemType& val  ///< [out] 結果を格納する変数')):
                writer.gen_vardecl(typename='Deconv',
                                   varname='deconv')
                writer.gen_return('deconv(obj, val)')
                
    def make_source(self, fout=sys.stdout):
        """ソースファイルを出力する．"""
        
        # テンプレートファイルは同じディレクトリにあると仮定している．
        template_file = self.template_file("PyCustom.cc")

        writer = CxxWriter(fout=fout)
        with open(template_file, 'rt') as fin:
            for line in fin:
                # 余分な改行を削除
                line = line.rstrip()

                if line == '%%INCLUDES%%':
                    # インクルードファイルの置換
                    for filename in self.source_include_files:
                        writer.gen_include(filename)
                    continue

                if line == '%%BEGIN_NAMESPACE%%':
                    # 名前空間の開始
                    if self.namespace is not None:
                        writer.write_line(f'BEGIN_NAMESPACE_{self.namespace}')
                    continue

                if line == '%%END_NAMESPACE%%':
                    # 名前空間の終了
                    if self.namespace is not None:
                        writer.write_line(f'END_NAMESPACE_{self.namespace}')
                    continue

                if line == '%%EXTRA_CODE%%':
                    self.make_extra_code(writer)
                    continue

                result = self.__tp_init_pat.match(line)
                if result:
                    # tp_XXX 設定の置換
                    writer.indent_set(len(result.group(1)))
                    self.make_tp_init(writer)
                    writer.indent_set(0)
                    continue

                result = self.__ex_init_pat.match(line)
                if result:
                    # 追加の初期化コードの置換
                    if self.__ex_init_gen is not None:
                        writer.indent_set(len(result.group(1)))
                        self.__ex_init_gen(writer)
                        writer.indent_set(0)
                    continue

                if line == '%%CONV_CODE%%':
                    # Conv 関数の置換
                    if self.__conv_gen is not None:
                        self.make_conv(writer)
                    continue

                if line == '%%DECONV_CODE%%':
                    # Deconv 関数の置換
                    if self.__deconv_gen is not None:
                        self.make_deconv(writer)
                    continue
                
                # 年の置換
                line = line.replace('%%Year%%', self.year())
                # クラス名の置換
                line = line.replace('%%Custom%%', self.classname)
                # Python 拡張用のクラス名の置換
                line = line.replace('%%PyCustom%%', self.pyclassname)
                # Python 上のタイプ名の置換
                line = line.replace('%%TypeName%%', self.pyname)
                # 名前空間の置換
                if self.namespace is not None:
                    line = line.replace('%%NAMESPACE%%', self.namespace)
                # タイプクラス名の置換
                line = line.replace('%%CustomType%%', self.typename)
                # オブジェクトクラス名の置換
                line = line.replace('%%CustomObject%%', self.objectname)

                writer.write_line(line)

    def make_extra_code(self, writer):
        if self.__preamble_gen is not None:
            self.__preamble_gen(writer)
        gen_func(self.__dealloc_gen, writer,
                 description='終了関数')
        gen_func(self.__repr_gen, writer, 
                 description='repr 関数')
        writer.gen_number(self.__number_gen, self.__number_name)
        writer.gen_sequence(self.__sequence_gen, self.__sequence_name)
        writer.gen_mapping(self.__mapping_gen, self.__mapping_name)
        gen_func(self.__hash_gen, writer, 
                 description='hash 関数')
        gen_func(self.__call_gen, writer,
                 description='call 関数')
        gen_func(self.__str_gen, writer, 
                 description='str 関数')
        gen_func(self.__richcompare_gen, writer,
                 description='richcompare 関数')
        writer.gen_methods(self.__method_gen, self.__method_name)
        writer.gen_getset(self.__getset_gen, self.__getset_name)
        gen_func(self.__init_gen, writer,
                 description='init 関数')
        gen_func(self.__new_gen, writer,
                 description='new 関数')
        
    def make_tp_init(self, writer):
        tp_list = []
        tp_list.append(('name', f'"{self.pyname}"'))
        tp_list.append(('basicsize', self.basicsize))
        tp_list.append(('itemsize', self.itemsize))
        if self.__dealloc_gen is not None:
            tp_list.append(('dealloc', self.__dealloc_gen.name))
        if self.__repr_gen is not None:
            tp_list.append(('repr', self.__repr_gen.name))
        if self.__number_name is not None:
            tp_list.append(('as_number', self.__number_name))
        if self.__sequence_name is not None:
            tp_list.append(('as_sequence', self.__sequence_name))
        if self.__mapping_name is not None:
            tp_list.append(('as_mapping', self.__mapping_name))
        if self.__hash_gen is not None:
            tp_list.append(('hash', self.__hash_gen.name))
        if self.__call_gen is not None:
            tp_list.append(('call', self.__call_gen.name))
        if self.__str_gen is not None:
            tp_list.append(('str', self.__str_gen.name))
        tp_list.append(('flags', self.flags))
        tp_list.append(('doc', f'PyDoc_STR("{self.doc_str}")'))
        if self.__richcompare_gen is not None:
            tp_list.append(('richcompare', self.__richcompare_gen.name))
        tp_list.append(('methods', self.__method_name))
        tp_list.append(('getset', self.__getset_name))
        if self.__init_gen is not None:
            tp_list.append(('init', self.__init_gen.name))
        if self.__new_gen is not None:
            tp_list.append(('new', self.__new_gen.name))
        for name, rval in tp_list:
            writer.gen_assign(f'{self.typename}.tp_{name}', f'{rval}')

    def make_conv(self, writer):
        description = f'{self.classname} を PyObject に変換する．'
        func_name = f'{self.pyclassname}::Conv::operator()'
        args = (f'const {self.classname}& val', )
        with writer.gen_func_block(description=description,
                                   return_type='PyObject*',
                                   func_name=func_name,
                                   args=args):
            writer.gen_auto_assign('type', f'{self.pyclassname}::_typeobject()')
            writer.gen_auto_assign('obj', 'type->tp_alloc(type, 0)')
            writer.gen_auto_assign('obj1', f'reinterpret_cast<{self.objectname}*>(obj)')
            self.__conv_gen(writer)
            writer.gen_return('obj')

    def make_deconv(self, writer):
        description = f'PyObject を {self.classname} に変換する．'
        func_name = f'{self.pyclassname}::Deconv::operator()'
        args = ('PyObject* obj',
                f'{self.classname}& val')
        with writer.gen_func_block(description=description,
                                   return_type='bool',
                                   func_name=func_name,
                                   args=args):
            self.__deconv_gen(writer)
    
    def __complete(self, name, default_name):
        """名前がない場合に名前を補完する．
        """
        if name is None:
            name = default_name
        return self.__check_name(name)

    def __check_name(self, name):
        """名前が重複していないかチェックする．

        重複していたら例外を送出する．
        """
        if name in self.__name_dict:
            raise ValueError(f'{name} is already in use')
        self.__name_dict.add(name)
        return name

    @staticmethod
    def year():
        """現在の年を表す文字列を返す．
        """
        return str(datetime.datetime.now().year)

    @staticmethod
    def template_file(filename):
        """テンプレートファイル名を返す．
        """
        basedir = os.path.dirname(__file__)
        return os.path.join(basedir, filename)

    def gen_obj_conv(self, writer, *,
                     objname='self',
                     varname):
        """PyObject* から自分のオブジェクト型に変換するコードを生成する．
        """
        writer.gen_auto_assign(varname,
                               f'reinterpret_cast<{self.objectname}*>({objname})')

    def gen_ref_conv(self, writer, *,
                     objname='self',
                     refname):
        """PyObject* から値の参照を取り出すコードを生成する．
        """
        writer.gen_autoref_assign(refname,
                                  f'{self.pyclassname}::_get_ref({objname})')
