#! /usr/bin/env python3

""" ModuleGen のクラス定義ファイル

:file: module_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

import re
import sys
from .genbase import GenBase
from .genbase import IncludesGen, BeginNamespaceGen, EndNamespaceGen
from .method_gen import MethodGen
from .cxxwriter import CxxWriter


class ExtraCodeGen:
    """%%EXTRA_CODE%% の置換を行う．
    """

    def __init__(self, gen):
        self.__gen = gen

    def __call__(self, line, writer):
        if line == '%%EXTRA_CODE%%':
            self.__gen.make_extra_code(writer)
            return True
        return False


class InitCodeGen:
    """%%INIT_CODE%% の置換を行う．
    """

    def __init__(self, gen):
        self.__gen = gen
        self.__init_pat = re.compile('^(\s*)%%INIT_CODE%%$')

    def __call__(self, line, writer):
        result = self.__init_pat.match(line)
        if result:
            writer.indent_set(len(result.group(1)))
            self.__gen.make_init_code(writer)
            writer.indent_set(0)
            return True
        return False
    

class ModuleGen(GenBase):
    """Python モジュールの初期化コードを生成するクラス
    """

    def __init__(self, *,
                 modulename,
                 namespace=None,
                 doc_str='',
                 include_files=[],
                 submodule_list=[],
                 pyclass_list=[],
                 ex_init=None):
        super().__init__()
        self.modulename = modulename
        self.namespace = namespace
        self.doc_str = doc_str

        # インクルードファイルのリスト
        self.__include_files = include_files
        
        # メソッド構造体の定義
        # モジュール定義の場合は関数がなくても空のテーブルを津kる．
        tbl_name = self.check_name('methods')
        self.__method_gen = MethodGen(self, tbl_name, module_func=True)

        # サブモジュールのリスト
        self.__submodule_list = submodule_list

        # Python 拡張クラスのリスト
        self.__pyclass_list = pyclass_list
        
        # 追加の初期化コード
        self.__ex_init_gen = ex_init

    def add_method(self, name, *,
                   func_name=None,
                   arg_list=[],
                   func_body=None,
                   doc_str=''):
        """メソッド定義を追加する．
        """
        # デフォルトの関数名は Python のメソッド名をそのまま用いる．
        func_name = self.complete_name(func_name, name)
        self.__method_gen.add(func_name,
                              name=name,
                              arg_list=arg_list,
                              is_static=False,
                              func_body=func_body,
                              doc_str=doc_str)

    def add_submodule(self, name, init_func):
        """サブモジュールを追加する．
        """
        self.__submodule_list.append((name, init_func))

    def make_header(self, fout=sys.stdout):
        """ヘッダファイルを出力する．
        """

        # Generator リスト
        gen_list = []
        #gen_list.append(IncludesGen(self.header_include_files))
        gen_list.append(BeginNamespaceGen(self.namespace))
        gen_list.append(EndNamespaceGen(self.namespace))

        # 置換リスト
        replace_list = []
        # 年の置換
        replace_list.append(('%%Year%%', self.year()))
        # モジュール名の置換
        replace_list.append(('%%ModuleName%%', self.modulename))
        # インタロック用のモジュール名の置換
        replace_list.append(('%%CapModuleName%%',
                             self.modulename.upper()))
        
        # テンプレートファイルは同じディレクトリにあると仮定している．
        template_file = self.template_file('custom_module.cc')

        writer = CxxWriter(fout=fout)
        self.make_file(template_file=self.template_file('custom.h'),
                       writer=CxxWriter(fout=fout),
                       gen_list=gen_list,
                       replace_list=replace_list)
        
    def make_source(self, fout=sys.stdout):
        """モジュールの定義ファイルを出力する．
        """

        # Generator リスト
        gen_list = []
        gen_list.append(IncludesGen(self.__include_files))
        gen_list.append(BeginNamespaceGen(self.namespace))
        gen_list.append(EndNamespaceGen(self.namespace))
        gen_list.append(ExtraCodeGen(self))
        gen_list.append(InitCodeGen(self))

        # 置換リスト
        replace_list = []
        # 年の置換
        replace_list.append(('%%Year%%', self.year()))
        # モジュール名の置換
        replace_list.append(('%%ModuleName%%', self.modulename))
        # DOC_STR の置換
        replace_list.append(('%%DOC_STR%%', self.doc_str))
        # 名前空間の置換
        if self.namespace is not None:
            replace_list.append(('%%NAMESPACE%%', self.namespace))
        
        # テンプレートファイルは同じディレクトリにあると仮定している．
        template_file = self.template_file('custom_module.cc')

        # 結果のファイル名
        source_file = f'{self.modulename}_module.cc'

        writer = CxxWriter(fout=fout)
        self.make_file(template_file=self.template_file('custom_module.cc'),
                       writer=CxxWriter(fout=fout),
                       gen_list=gen_list,
                       replace_list=replace_list)

    def make_extra_code(self, writer):
        if self.__method_gen is not None:
            self.__method_gen(writer)

    def make_init_code(self, writer):
        # サブモジュールの登録
        if len(self.__submodule_list) > 0:
            writer.gen_CRLF()
        for name, init_func in self.__submodule_list:
            with writer.gen_if_block(f'!PyModule::reg_submodule(m, "{name}", {init_func}())'):
                writer.write_line('goto error;')

        # 拡張クラスの登録
        if len(self.__pyclass_list) > 0:
            writer.gen_CRLF()
        for pyclass in self.__pyclass_list:
            with writer.gen_if_block(f'!{pyclass}::init(m)'):
                writer.write_line('goto error;')

        # 追加の初期化コード
        if self.__ex_init_gen is not None:
            self.__ex_init_gen(writer)
