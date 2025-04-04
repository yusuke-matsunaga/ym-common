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
        self.__method_name = self.check_name('methods')
        self.__method_gen = MethodGen()

        # get/set 構造体の定義
        self.__getset_name = self.check_name('getsets')
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

    def add_preamble(self, func_body):
        if self.__preamble_gen is not None:
            raise ValueError("preamble has benn already defined")
        self.__preamble_gen = func_body
        
    def add_dealloc(self, *,
                    func_name=None,
                    dealloc_func='default'):
        """dealloc 関数定義を追加する．
        """
        if self.__dealloc_gen is not None:
            raise ValueError('dealloc has been already defined')
        func_name = self.complete_name(func_name, 'dealloc_func')
        self.__dealloc_gen = DeallocGen(self, func_name, dealloc_func)

    def add_repr(self, *,
                 func_name=None,
                 repr_func=None):
        """repr 関数定義を追加する．
        """
        if self.__repr_gen is not None:
            raise ValueError('repr has been already defined')
        func_name = self.complete_name(func_name, 'repr_func')
        self.__repr_gen = ReprFuncGen(self, func_name, repr_func)

    def add_hash(self, *,
                 func_name=None,
                 hash_func=None):
        """hash 関数定義を追加する．
        """
        if self.__hash_gen is not None:
            raise ValueError('hash has been already defined')
        func_name = self.complete_name(func_name, 'hash_func')
        self.__hash_gen = HashFuncGen(self, func_name, hash_func)

    def add_ex_init(self, gen_body):
        if self.__ex_init_gen is not None:
            raise ValueError('ex_init has been already defined')
        self.__ex_init_gen = gen_body
                    
    def add_call(self, *,
                 func_name=None,
                 call_func=None,
                 arg_list=[]):
        """call 関数定義を追加する．
        """
        if self.__call_gen is not None:
            raise ValueError('hash has been already defined')
        func_name = self.complete_name(func_name, 'call_func')
        self.__call_gen = CallFuncGen(self, func_name, call_func, arg_list)

    def add_str(self, *,
                func_name=None,
                str_func=None):
        """str 関数定義を追加する．
        """
        if self.__str_gen is not None:
            raise ValueError('str has been already defined')
        func_name = self.complete_name(func_name, 'str_func')
        self.__str_gen = ReprFuncGen(self, func_name, str_func)

    def add_richcompare(self, *,
                        func_name=None,
                        cmp_func=None):
        """richcompare 関数定義を追加する．
        """
        if self.__richcompare_gen is not None:
            raise ValueError('richcompare has been already defined')
        func_name = self.complete_name(func_name, 'richcompare_func')
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
        self.__number_name = self.complete_name(name, 'number')
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
        self.__sequence_name = self.complete_name(name, 'sequence')
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
        self.__mapping_name = self.complete_name(name, 'mapping')
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
        func_name = self.complete_name(func_name, 'init_func')
        self.__init_gen = InitProcGen(self, func_name, func_body, arg_list)
        
    def add_new(self, *,
                func_name=None,
                func_body=None,
                arg_list=[]):
        """new 関数定義を追加する．
        """
        if self.__new_gen is not None:
            raise ValueError('new has been already defined')
        func_name = self.complete_name(func_name, 'new_func')
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
        func_name = self.complete_name(func_name, name)
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
        self.check_name(func_name)
        self.__getset_gen.add_getter(self, func_name,
                                     has_closure=has_closure,
                                     func_body=func_body)

    def add_setter(self, func_name, *,
                   has_closure=False,
                   func_body=None):
        """setter 定義を追加する．
        """
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
        self.__getset_gen.add_attr(name,
                                   getter_name=getter_name,
                                   setter_name=setter_name,
                                   closure=closure,
                                   doc_str=doc_str)
    
    def add_conv(self, body):
        self.__conv_gen = ConvGen(self, body)

    def add_deconv(self, body, *,
                   extra_func=None):
        self.__deconv_gen = DeconvGen(self, body, extra_func=extra_func)

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
            writer.gen_vardecl(typename='ElemType', varname='val')
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
        if self.__preamble_gen is not None:
            self.__preamble_gen(writer)
        gen_func(self.__dealloc_gen, writer,
                 comment='終了関数')
        gen_func(self.__repr_gen, writer, 
                 comment='repr 関数')
        writer.gen_number(self.__number_gen, self.__number_name)
        writer.gen_sequence(self.__sequence_gen, self.__sequence_name)
        writer.gen_mapping(self.__mapping_gen, self.__mapping_name)
        gen_func(self.__hash_gen, writer, 
                 comment='hash 関数')
        gen_func(self.__call_gen, writer,
                 comment='call 関数')
        gen_func(self.__str_gen, writer, 
                 comment='str 関数')
        gen_func(self.__richcompare_gen, writer,
                 comment='richcompare 関数')
        self.__method_gen(writer, self.__method_name)
        self.__getset_gen(writer, self.__getset_name)
        gen_func(self.__init_gen, writer,
                 comment='init 関数')
        gen_func(self.__new_gen, writer,
                 comment='new 関数')
        
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
