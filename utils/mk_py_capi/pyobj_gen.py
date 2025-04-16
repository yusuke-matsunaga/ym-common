#! /usr/bin/env python3

""" PyObjGen のクラス定義ファイル

:file: pyobj_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

import re
import sys
from .genbase import GenBase, IncludesGen, BeginNamespaceGen, EndNamespaceGen
from .funcgen import DeallocGen
from .funcgen import ReprFuncGen
from .funcgen import HashFuncGen
from .funcgen import CallFuncGen
from .funcgen import StrFuncGen
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
from .funcgen import ConvGen
from .funcgen import DeconvGen
from .number_gen import NumberGen
from .sequence_gen import SequenceGen
from .mapping_gen import MappingGen
from .method_gen import MethodGen
from .getset_gen import GetSetGen
from .utils import gen_func
from .cxxwriter import CxxWriter
    

class ConvDefGen:
    """%%CONV_DEF%% の置換を行うクラス
    """
    
    def __init__(self, conv_gen, deconv_gen):
        self.__conv_def_pat = re.compile('^(\s*)%%CONV_DEF%%$')
        self.__conv_gen = conv_gen
        self.__deconv_gen = deconv_gen

    def __call__(self, line, writer):
        result = self.__conv_def_pat.match(line)
        if result:
            # Conv の宣言
            writer.indent_set(len(result.group(1)))
            if self.__conv_gen is None:
                writer.gen_CRLF()
                if self.__deconv_gen is None:
                    writer.gen_comment('このクラスは Conv/Deconv を持たない．')
                else:
                    writer.gen_comment('このクラスは Conv を持たない．')
            else:
                self.__conv_gen.gen_decl(writer)
            writer.indent_set(0)

            # Deconv の宣言
            writer.indent_set(len(result.group(1)))
            if self.__deconv_gen is None:
                if self.__conv_gen is not None:
                    writer.gen_CRLF()
                    writer.gen_comment('このクラスは Deconv を持たない．')
            else:
                self.__deconv_gen.gen_decl(writer)
            writer.indent_set(0)
            return True
        return False


class ToDefGen:
    """%%TOPYOBJECT%% の置換を行うクラス
    """
    
    def __init__(self, conv_gen, deconv_gen):
        self.__to_def_pat = re.compile('^(\s*)%%TOPYOBJECT%%$')
        self.__conv_gen = conv_gen
        self.__deconv_gen = deconv_gen

    def __call__(self, line, writer):
        result = self.__to_def_pat.match(line)
        if result:
            # ToPyObject の宣言
            if self.__conv_gen is not None:
                writer.indent_set(len(result.group(1)))
                self.__conv_gen.gen_tofunc(writer)
                writer.indent_set(0)
            # FromPyObject の宣言
            if self.__deconv_gen is not None:
                writer.indent_set(len(result.group(1)))
                self.__deconv_gen.gen_fromfunc(writer)
                writer.indent_set(0)
            return True
        return False

    
class GetDefGen:
    """%%GET_DEF%% の置換を行うクラス
    """

    def __init__(self, gen):
        self.__get_def_pat = re.compile('^(\s*)%%GET_DEF%%')
        self.__gen = gen

    def __call__(self, line, writer):
        result = self.__get_def_pat.match(line)
        if result:
            writer.indent_set(len(result.group(1)))
            self.__gen.make_get_def(writer)
            writer.indent_set(0)
            return True
        return False

    
class ExtraCodeGen:
    """%%EXTRA_CODE%% の置換を行うクラス
    """
    
    def __init__(self, gen):
        self.__gen = gen

    def __call__(self, line, writer):
        if line == '%%EXTRA_CODE%%':
            self.__gen.make_extra_code(writer)
            return True
        return False


class TpInitGen:
    """%%TP_INIT_CDE%% の置換を行うクラス
    """

    def __init__(self, gen):
        self.__gen = gen
        self.__tp_init_pat = re.compile('^(\s*)%%TP_INIT_CODE%%$')

    def __call__(self, line, writer):
        result = self.__tp_init_pat.match(line)
        if result:
            # tp_XXX 設定の置換
            writer.indent_set(len(result.group(1)))
            self.__gen.make_tp_init(writer)
            writer.indent_set(0)
            return True
        return False


class ExInitGen:
    """%%EX_INIT_CODE%% の置換を行うクラス
    """

    def __init__(self, gen):
        self.__gen = gen
        self.__ex_init_pat = re.compile('^(\s*)%%EX_INIT_CODE%%$')

    def __call__(self, line, writer):
        result = self.__ex_init_pat.match(line)
        if result:
            # 追加の初期化コードの置換
            writer.indent_set(len(result.group(1)))
            self.__gen.make_ex_init(writer)
            writer.indent_set(0)
            return True
        return False


class ConvCodeGen:
    """%%CONV_CODE%% の置換を行うクラス
    """

    def __init__(self, gen):
        self.__gen = gen

    def __call__(self, line, writer):
        if line == '%%CONV_CODE%%':
            self.__gen.make_conv_code(writer)
            return True
        return False
    

class PyObjGen(GenBase):
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
        super().__init__()
        
        # C++ のクラス名
        self.classname = classname
        # Python-CAPI 用のクラス名
        if pyclassname is None:
            pyclassname = f'Py{classname}'
        self.pyclassname = pyclassname
        # 名前空間
        self.namespace = namespace
        # Python-CAPI 用のタイプクラス名
        if typename is None:
            typename = f'{pyname}_Type'
        self.typename = typename
        # Python-CAPI 用のオブジェクトクラス名
        if objectname is None:
            objectname = f'{pyname}_Object'
        self.objectname = objectname
        # Python のクラス名
        self.pyname = pyname
        
        # ヘッダファイル用のインクルードファイルリスト
        self.header_include_files = header_include_files
        # ソースファイル用のインクルードファイルリスト
        self.source_include_files = source_include_files

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
        self.__number_gen = None

        # Sequence 構造体の定義
        self.__sequence_gen = None

        # Mapping 構造体の定義
        self.__mapping_gen = None

        # メソッド構造体の定義
        self.__method_gen = None

        # get/set 構造体の定義
        self.__getset_gen = None

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
        self.doc_str = f'Python extended object for {self.classname}'

    def add_preamble(self, func_body):
        if self.__preamble_gen is not None:
            raise ValueError("preamble has benn already defined")
        self.__preamble_gen = func_body
        
    def add_dealloc(self, func_body='default', *,
                    func_name=None):
        """dealloc 関数定義を追加する．
        """
        if self.__dealloc_gen is not None:
            raise ValueError('dealloc has been already defined')
        func_name = self.complete_name(func_name, 'dealloc_func')
        self.__dealloc_gen = DeallocGen(self, func_name, func_body)

    def add_repr(self, func_body=None, *,
                 func_name=None):
        """repr 関数定義を追加する．
        """
        if self.__repr_gen is not None:
            raise ValueError('repr has been already defined')
        func_name = self.complete_name(func_name, 'repr_func')
        self.__repr_gen = ReprFuncGen(self, func_name, func_body)

    def add_hash(self, func_body=None, *,
                 func_name=None):
        """hash 関数定義を追加する．
        """
        if self.__hash_gen is not None:
            raise ValueError('hash has been already defined')
        func_name = self.complete_name(func_name, 'hash_func')
        self.__hash_gen = HashFuncGen(self, func_name, func_body)

    def add_ex_init(self, gen_body):
        if self.__ex_init_gen is not None:
            raise ValueError('ex_init has been already defined')
        self.__ex_init_gen = gen_body
                    
    def add_call(self, func_body=None, *,
                 func_name=None,
                 arg_list=[]):
        """call 関数定義を追加する．
        """
        if self.__call_gen is not None:
            raise ValueError('hash has been already defined')
        func_name = self.complete_name(func_name, 'call_func')
        self.__call_gen = CallFuncGen(self, func_name, func_body, arg_list)

    def add_str(self, func_body=None, *,
                func_name=None):
        """str 関数定義を追加する．
        """
        if self.__str_gen is not None:
            raise ValueError('str has been already defined')
        func_name = self.complete_name(func_name, 'str_func')
        self.__str_gen = StrFuncGen(self, func_name, func_body)

    def add_richcompare(self, func_body=None, *,
                        func_name=None):
        """richcompare 関数定義を追加する．
        """
        if self.__richcompare_gen is not None:
            raise ValueError('richcompare has been already defined')
        func_name = self.complete_name(func_name, 'richcompare_func')
        self.__richcompare_gen = RichcmpFuncGen(self, func_name, func_body)

    def add_nb_add(self, *,
                   func_name=None,
                   expr='default',
                   op_list1=[],
                   op_list2=[]):
        """nb_add の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_add')
        self.__number_gen.add_add(func_name, expr=expr, op_list1=op_list1, op_list2=op_list2)

    def add_nb_subtract(self, *,
                        func_name=None,
                        expr='default',
                        op_list1=[],
                        op_list2=[]):
        """nb_subtract の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_subtract')
        self.__number_gen.add_subtract(func_name, expr=expr, op_list1=op_list1, op_list2=op_list2)

    def add_nb_multiply(self, *,
                        func_name=None,
                        expr='default',
                        op_list1=[],
                        op_list2=[]):
        """nb_multiply の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_multiply')
        self.__number_gen.add_multiply(func_name, expr=expr, op_list1=op_list1, op_list2=op_list2)

    def add_nb_remainder(self, *,
                         func_name=None,
                         expr='default',
                         op_list1=[],
                         op_list2=[]):
        """nb_remainder の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_remainder')
        self.__number_gen.add_remainder(func_name, expr=expr, op_list1=op_list1, op_list2=op_list2)

    def add_nb_divmod(self, *,
                      func_name=None,
                      expr='default',
                      op_list1=[],
                      op_list2=[]):
        """nb_divmod の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_divmod')
        self.__number_gen.add_divmod(func_name, expr=expr, op_list1=op_list1, op_list2=op_list2)

    def add_nb_power(self, *,
                     func_name=None,
                     body):
        """nb_power の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_power')
        self.__number_gen.add_power(func_name, op_list1=op_list1, op_list2=op_list2)

    def add_nb_negative(self, *,
                        func_name=None,
                        body):
        """nb_negative の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_negative')
        self.__number_gen.add_negative(self.new_unaryfunc(func_name, body))

    def add_nb_positive(self, *,
                        func_name=None,
                        body):
        """nb_positive の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_positive')
        self.__number_gen.add_positive(self.new_unaryfunc(func_name, body))

    def add_nb_absolute(self, *,
                        func_name=None,
                        body):
        """nb_absolute の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_absolute')
        self.__number_gen.add_absolute(self.new_unaryfunc(func_name, body))

    def add_nb_bool(self, *,
                    func_name=None,
                    body):
        """nb_bool の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_bool')
        self.__number_gen.add_bool(self.new_unaryfunc(func_name, body))

    def add_nb_invert(self, *,
                      func_name=None,
                      body='default'):
        """nb_invert の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_invert')
        if body == 'default':
            def invert_body(writer):
                writer.gen_return_pyobject(self.pyclassname, '~val')
            body = invert_body
        self.__number_gen.add_invert(self.new_unaryfunc(func_name, body))

    def add_nb_lshift(self, *,
                      func_name=None,
                      expr='default',
                      op_list1=[]):
        """nb_lshift の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_lshift')
        self.__number_gen.add_lshift(func_name, expr=expr, op_list1=op_list1)

    def add_nb_rshift(self, *,
                      func_name=None,
                      expr='default',
                      op_list1=[]):
        """nb_rshift の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_rshift')
        self.__number_gen.add_rshift(func_name, expr=expr, op_list1=op_list1)

    def add_nb_and(self, *,
                   func_name=None,
                   expr='default',
                   op_list1=[],
                   op_list2=[]):
        """nb_and の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_and')
        self.__number_gen.add_and(func_name, expr=expr, op_list1=op_list1, op_list2=op_list2)

    def add_nb_xor(self, *,
                   func_name=None,
                   expr='default',
                   op_list1=[],
                   op_list2=[]):
        """nb_xor の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_xor')
        self.__number_gen.add_xor(func_name, expr=expr, op_list1=op_list1, op_list2=op_list2)

    def add_nb_or(self, *,
                  func_name=None,
                  expr='default',
                  op_list1=[],
                  op_list2=[]):
        """nb_or の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_or')
        self.__number_gen.add_or(func_name, expr=expr, op_list1=op_list1, op_list2=op_list2)

    def add_nb_int(self, *,
                   func_name=None,
                   body):
        """nb_int の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_int')
        self.__number_gen.add_int(self.new_unaryfunc(func_name, body))

    def add_nb_float(self, *,
                     func_name=None,
                     body):
        """nb_float の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_float')
        self.__number_gen.add_float(self.new_unaryfunc(func_name, body))

    def add_nb_inplace_add(self, *,
                           func_name=None,
                           stmt=None,
                           op_list1=[]):
        """nb_inplace_add の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_add')
        self.__number_gen.add_inplace_add(func_name, stmt=stmt, op_list1=op_list1)

    def add_nb_inplace_subtract(self, *,
                                func_name=None,
                                stmt=None,
                                op_list1=[]):
        """nb_inplace_subtract の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_subtract')
        self.__number_gen.add_inplace_subtract(func_name, stmt=stmt, op_list1=op_list1)

    def add_nb_inplace_multiply(self, *,
                                func_name=None,
                                stmt=None,
                                op_list1=[]):
        """nb_inplace_multiply の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_multiply')
        self.__number_gen.add_inplace_multiply(func_name, stmt=stmt, op_list1=op_list1)

    def add_nb_inplace_remainder(self, *,
                                 func_name=None,
                                 stmt=None,
                                 op_list1=[]):
        """nb_inplace_remainder の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_remainder')
        self.__number_gen.add_inplace_remainder(func_name, stmt=stmt, op_list1=op_list1)

    def add_nb_inplace_power(self, *,
                             func_name=None,
                             stmt=None,
                             body):
        """nb_inplace_power の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_power')
        self.__number_gen.add_inplace_power(func_name, stmt=stmt, op_list1=op_list1)

    def add_nb_inplace_lshift(self, *,
                              func_name=None,
                              stmt=None,
                              op_list1=[]):
        """nb_inplace_lshift の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_lshift')
        self.__number_gen.add_inplace_lshift(func_name, stmt=stmt, op_list1=op_list1)
        
    def add_nb_inplace_rshift(self, *,
                              func_name=None,
                              stmt=None,
                              op_list1=[]):
        """nb_inplace_rshift の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_rshift')
        self.__number_gen.add_inplace_rshift(func_name, stmt=stmt, op_list1=op_list1)

    def add_nb_inplace_and(self, *,
                           func_name=None,
                           stmt=None,
                           op_list1=[]):
        """nb_inplace_and の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_and')
        self.__number_gen.add_inplace_and(func_name, stmt=stmt, op_list1=op_list1)

    def add_nb_inplace_xor(self, *,
                           func_name=None,
                           stmt=None,
                           op_list1=[]):
        """nb_inplace_xor の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_xor')
        self.__number_gen.add_inplace_xor(func_name, stmt=stmt, op_list1=op_list1)

    def add_nb_inplace_or(self, *,
                          func_name=None,
                          stmt=None,
                          op_list1=[]):
        """nb_inplace_or の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_or')
        self.__number_gen.add_inplace_or(func_name, stmt=stmt, op_list1=op_list1)

    def add_nb_floor_divide(self, *,
                            func_name=None,
                            expr='default',
                            op_list1=[],
                            op_list2=[]):
        """nb_floor_divide の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_floor_divide')
        self.__number_gen.add_floor_divide(func_name, expr=expr, op_list1=op_list1, op_list2=op_list2)

    def add_nb_true_divide(self, *,
                           func_name=None,
                           expr='default',
                           op_list1=[],
                           op_list2=[]):
        """nb_true_divide の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_true_divide')
        self.__number_gen.add_true_divide(func_name, expr=expr, op_list1=op_list1, op_list2=op_list2)

    def add_nb_inplace_floor_divide(self, *,
                                    func_name=None,
                                    stmt=None,
                                    op_list1=[]):
        """nb_inplace_floor_divide の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_floor_divide')
        self.__number_gen.add_inplace_floor_divide(func_name, stmt=stmt, op_list1=op_list1)

    def add_nb_inplace_true_divide(self, *,
                                   func_name=None,
                                   stmt=None,
                                   op_list1=[]):
        """nb_inplace_true_divide の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_true_divide')
        self.__number_gen.add_inplace_true_divide(func_name, stmt=stmt, op_list1=op_list1)

    def add_nb_index(self, *,
                     func_name=None,
                     body):
        """nb_index の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_index')
        self.__number_gen.add_index(self.new_unaryfunc(func_name, body))

    def add_nb_matrix_multiply(self, *,
                               func_name=None,
                               expr='default',
                               op_list1=[],
                               op_list2=[]):
        """nb_matrix_multiply の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_matrix_multiply')
        self.__number_gen.add_matrix_multiply(func_name, expr=expr, op_list1=op_list1, op_list2=op_list2)

    def add_nb_inplace_matrix_multiply(self, *,
                                       func_name=None,
                                       stmt=None,
                                       op_list1=[]):
        """nb_inplace_matrix_multiply の関数定義を追加する．
        """
        self.__check_number()
        func_name = self.complete_name(func_name, 'nb_inplace_matrix_multiply')
        self.__number_gen.add_inplace_matrix_multiply(func_name, stmt=stmt, op_list1=op_list1)
        
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
        name = self.complete_name(name, 'sequence')
        self.__sequence_gen = SequenceGen(
            self, name,
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
        name = self.complete_name(name, 'mapping')
        self.__mapping_gen = MappingGen(
            self, name,
            mp_length=mp_length,
            mp_subscript=mp_subscript,
            mp_ass_subscript=mp_ass_subscript)
        
    def add_init(self, func_body=None, *,
                 func_name=None,
                 arg_list=[]):
        """init 関数定義を追加する．
        """
        if self.__init_gen is not None:
            raise ValueError('init has been already defined')
        func_name = self.complete_name(func_name, 'init_func')
        self.__init_gen = InitProcGen(self, func_name, func_body, arg_list)
        
    def add_new(self, func_body=None, *,
                func_name=None,
                arg_list=[]):
        """new 関数定義を追加する．
        """
        if self.__new_gen is not None:
            raise ValueError('new has been already defined')
        func_name = self.complete_name(func_name, 'new_func')
        self.__new_gen = NewFuncGen(self, func_name, func_body, arg_list)
        
    def add_method(self, name, *,
                   func_name=None,
                   func_body=None,
                   arg_list=[],
                   is_static=False,
                   doc_str=''):
        """メソッド定義を追加する．
        """
        if self.__method_gen is None:
            tbl_name = self.check_name('methods')
            self.__method_gen = MethodGen(self, tbl_name)
        # デフォルトの関数名は Python のメソッド名をそのまま用いる．
        func_name = self.complete_name(func_name, name)
        self.__method_gen.add(func_name,
                              name=name,
                              arg_list=arg_list,
                              is_static=is_static,
                              func_body=func_body,
                              doc_str=doc_str)
        
    def add_static_method(self, name, *,
                          func_name=None,
                          func_body=None,
                          arg_list=[],
                          doc_str=''):
        """スタティックメソッド定義を追加する．
        """
        self.add_method(name,
                        func_name=func_name,
                        func_body=func_body,
                        arg_list=arg_list,
                        is_static=True,
                        doc_str=doc_str)

    def add_getter(self, func_name, *,
                   func_body=None,
                   has_closure=False):
        """getter 定義を追加する．
        """
        self.__check_getset()
        self.check_name(func_name)
        self.__getset_gen.add_getter(self, func_name,
                                     has_closure=has_closure,
                                     func_body=func_body)

    def add_setter(self, func_name, *,
                   func_body=None,
                   has_closure=False):
        """setter 定義を追加する．
        """
        self.__check_getset()
        self.check_name(func_name)
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
        self.__check_getset()
        self.__getset_gen.add_attr(name,
                                   getter_name=getter_name,
                                   setter_name=setter_name,
                                   closure=closure,
                                   doc_str=doc_str)
    
    def add_conv(self, func_body):
        self.__conv_gen = ConvGen(self, func_body)

    def add_deconv(self, func_body, *,
                   extra_func=None,
                   error_value=None):
        self.__deconv_gen = DeconvGen(self, func_body,
                                      extra_func=extra_func,
                                      error_value=error_value)

    def new_lenfunc(self, name, body):
        return LenFuncGen(self, name, body)

    def new_inquiry(self, name, body):
        return InquiryGen(self, name, body)

    def new_unaryfunc(self, name, body):
        return UnaryFuncGen(self, name, body)

    def new_binaryfunc(self, name, body, *,
                       arg2name=None):
        return BinaryFuncGen(self, name, body,
                             arg2name=arg2name)

    def new_binop(self, name, *,
                  op_list1,
                  op_list2=[]):
        return BinOpFuncGen(self, name,
                            op_list1=op_list1,
                            op_list2=op_list2)
                          
    def new_ternaryfunc(self, name, body, *,
                        arg2name=None,
                        arg3name=None,
                        has_ref_conv=True):
        return TernaryFuncGen(self, name, body,
                              arg2name=arg2name,
                              arg3name=arg3name,
                              has_ref_conv=has_ref_conv)

    def new_nb_ternaryfunc(self, name, body):
        return self.new_ternaryfunc(name, body, has_ref_conv=False)
    
    def new_ssizeargfunc(self, name, body, *,
                         arg2name=None):
        return SsizeArgFuncGen(self, name, body,
                               arg2name=arg2name)

    def new_ssizeobjargproc(self, name, body, *,
                            arg2name=None,
                            arg3name=None):
        return SsizeObjArgProcGen(self, name, body,
                                  arg2name=arg2name,
                                  arg3name=arg3name)

    def new_objobjproc(self, name, body, *,
                       arg2name=None):
        return ObjObjProcGen(self, name, body,
                             arg2name=arg2name)

    def new_objobjargproc(self, name, body, *,
                          arg2name=None,
                          arg3name=None):
        return ObjObjArgProcGen(self, name, body,
                                arg2name=arg2name,
                                arg3name=arg3name)
                
    def make_header(self, fout=sys.stdout):
        """ヘッダファイルを出力する．"""

        # Generator リスト
        gen_list = []
        gen_list.append(IncludesGen(self.header_include_files))
        gen_list.append(BeginNamespaceGen(self.namespace))
        gen_list.append(EndNamespaceGen(self.namespace))
        gen_list.append(ConvDefGen(self.__conv_gen, self.__deconv_gen))
        gen_list.append(ToDefGen(self.__conv_gen, self.__deconv_gen))
        gen_list.append(GetDefGen(self))
        
        # 置換リスト
        replace_list = []
        # 年の置換
        replace_list.append(('%%Year%%', self.year()))
        # インタロック用マクロ名の置換
        replace_list.append(('%%PYCUSTOM%%', self.pyclassname.upper()))
        # クラス名の置換
        replace_list.append(('%%Custom%%', self.classname))
        # Python 拡張用のクラス名の置換
        replace_list.append(('%%PyCustom%%', self.pyclassname))
        # 名前空間の置換
        if self.namespace is not None:
            replace_list.append(('%%NAMESPACE%%', self.namespace))

        self.make_file(template_file=self.template_file('PyCustom.h'),
                       writer=CxxWriter(fout=fout),
                       gen_list=gen_list,
                       replace_list=replace_list)

    def make_get_def(self, writer):
        if self.__deconv_gen is None:
            return
        dox_comment = f'@brief PyObject から {self.classname} を取り出す．'
        with writer.gen_func_block(dox_comment=dox_comment,
                                   is_static=True,
                                   return_type='ElemType',
                                   func_name='Get',
                                   args=['PyObject* obj ///< [in] 対象の Python オブジェクト']):
            writer.gen_vardecl(typename='ElemType', varname='val',
                               initializer=self.__deconv_gen.error_value)
            with writer.gen_if_block(f'{self.pyclassname}::FromPyObject(obj, val)'):
                writer.gen_return('val')
            writer.gen_type_error(f'"Could not convert to {self.classname}"',
                                  noexit=True)
            writer.gen_return('val')
        
    def make_source(self, fout=sys.stdout):

        # Generator リスト
        gen_list = []
        gen_list.append(IncludesGen(self.source_include_files))
        gen_list.append(BeginNamespaceGen(self.namespace))
        gen_list.append(EndNamespaceGen(self.namespace))
        gen_list.append(ExtraCodeGen(self))
        gen_list.append(TpInitGen(self))
        gen_list.append(ExInitGen(self))
        gen_list.append(ConvCodeGen(self))
        
        # 置換リスト
        replace_list = []
        # 年の置換
        replace_list.append(('%%Year%%', self.year()))
        # クラス名の置換
        replace_list.append(('%%Custom%%', self.classname))
        # Python 拡張用のクラス名の置換
        replace_list.append(('%%PyCustom%%', self.pyclassname))
        # Python 上のタイプ名の置換
        replace_list.append(('%%TypeName%%', self.pyname))
        # 名前空間の置換
        if self.namespace is not None:
            replace_list.append(('%%NAMESPACE%%', self.namespace))
        # タイプクラス名の置換
        replace_list.append(('%%CustomType%%', self.typename))
        # オブジェクトクラス名の置換
        replace_list.append(('%%CustomObject%%', self.objectname))

        self.make_file(template_file=self.template_file('PyCustom.cc'),
                       writer=CxxWriter(fout=fout),
                       gen_list=gen_list,
                       replace_list=replace_list)

    def make_extra_code(self, writer):
        def gen_common(writer, gen):
            if gen is not None:
                gen(writer)
        gen_common(writer, self.__preamble_gen)
        gen_func(self.__dealloc_gen, writer,
                 comment='終了関数')
        gen_func(self.__repr_gen, writer, 
                 comment='repr 関数')
        gen_common(writer, self.__number_gen)
        gen_common(writer, self.__sequence_gen)
        gen_common(writer, self.__mapping_gen)
        gen_func(self.__hash_gen, writer, 
                 comment='hash 関数')
        gen_func(self.__call_gen, writer,
                 comment='call 関数')
        gen_func(self.__str_gen, writer, 
                 comment='str 関数')
        gen_func(self.__richcompare_gen, writer,
                 comment='richcompare 関数')
        gen_common(writer, self.__method_gen)
        gen_common(writer, self.__getset_gen)
        gen_func(self.__init_gen, writer,
                 comment='init 関数')
        gen_func(self.__new_gen, writer,
                 comment='new 関数')
        
    def make_tp_init(self, writer):
        def gen_tp(writer, tp_name, rval):
            writer.gen_assign(f'{self.typename}.tp_{tp_name}', rval)
        gen_tp(writer, 'name', f'"{self.pyname}"')
        gen_tp(writer, 'basicsize', self.basicsize)
        gen_tp(writer, 'itemsize', self.itemsize)
        if self.__dealloc_gen is not None:
            self.__dealloc_gen.gen_tp(writer)
        if self.__repr_gen is not None:
            self.__repr_gen.gen_tp(writer)
        if self.__number_gen is not None:
            self.__number_gen.gen_tp(writer)
        if self.__sequence_gen is not None:
            self.__sequence_gen.gen_tp(writer)
        if self.__mapping_gen is not None:
            self.__mapping_gen.gen_tp(writer)
        if self.__hash_gen is not None:
            self.__hash_gen.gen_tp(writer)
        if self.__call_gen is not None:
            self.__call_gen.gen_tp(writer)
        if self.__str_gen is not None:
            self.__str_gen.gen_tp(writer)
        gen_tp(writer, 'flags', self.flags)
        gen_tp(writer, 'doc', f'PyDoc_STR("{self.doc_str}")')
        if self.__richcompare_gen is not None:
            self.__richcompare_gen.gen_tp(writer)
        if self.__method_gen is not None:
            self.__method_gen.gen_tp(writer)
        if self.__getset_gen is not None:
            self.__getset_gen.gen_tp(writer)
        if self.__init_gen is not None:
            self.__init_gen.gen_tp(writer)
        if self.__new_gen is not None:
            self.__new_gen.gen_tp(writer)
    
    def make_ex_init(self, writer):
        if self.__ex_init_gen is not None:
            self.__ex_init_gen(writer)

    def make_conv_code(self, writer):
        # Conv 関数の置換
        if self.__conv_gen is not None:
            self.__conv_gen(writer)
        # Deconv 関数の置換
        if self.__deconv_gen is not None:
            self.__deconv_gen(writer)

    def gen_alloc_code(self, writer, *,
                       varname='self'):
        """PyObject* の拡張クラスの領域を確保するコードを出力する．

        ただし，Cタイプの allocate なので初期化はされていない．
        """
        writer.gen_auto_assign('type', f'{self.pyclassname}::_typeobject()')
        writer.gen_auto_assign(f'{varname}', 'type->tp_alloc(type, 0)')

    def gen_raw_conv(self, writer, *,
                     varname='val'):
        """PyObject* self から classname& val に変換するコードを出力する．

        変換が成功したら true を返す．
        失敗したら以下のコードに制御を移す．
        """
        with writer.gen_if_block(f'{self.pyclassname}::Check(obj)'):
            writer.gen_assign(varname, f'{self.pyclassname}::_get_ref(obj)')
            writer.gen_return('true')
        
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
            
    def __check_number(self):
        if self.__number_gen is None:
            name = self.check_name('number')
            self.__number_gen = NumberGen(self, name)

    def __check_getset(self):
        if self.__getset_gen is None:
            name = self.check_name('getsets')
            self.__getset_gen = GetSetGen(self, name)
