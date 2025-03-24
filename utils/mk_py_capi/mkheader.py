#! /usr/bin/env python3

""" MkHeader のクラス定義ファイル

:file: mkheader.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from mk_py_capi.mkbase import MkBase
import sys


class MkHeader(MkBase):
    """Python 拡張用のヘッダファイルを生成するためのクラス
    """

    def __init__(self, *,
                 fout=sys.stdout,
                 classname,
                 pyclassname,
                 namespace,
                 include_files=None):
        super().__init__(fout=fout,
                         classname=classname,
                         pyclassname=pyclassname,
                         namespace=namespace)
        self.include_files = include_files

    def __call__(self):
        """ヘッダファイルを出力する．"""

        # テンプレートファイルは同じディレクトリにあると仮定している．
        template_file = self.template_file("PyCustom.h")

        # 結果のヘッダファイル名
        header_file = f'{self.pyclassname}.h'

        # インタロック用マクロ名
        cap_header_file = self.pyclassname.upper()

        with open(template_file, 'rt') as fin:
            for line in fin:
                # 余分な改行を削除
                line = line.rstrip()

                if line == '%%INCLUDES%%':
                    # インクルードファイルの置換
                    for filename in self.include_files:
                        self._write_line(f'#include "{filename}"')
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
                line = line.replace('%%NAMESPACE%%', self.namespace)

                self._write_line(line)

                
if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(
        prog='mk_header',
        description='make header file for Python extention')
    parser.add_argument('classname')
    parser.add_argument('namespace')
    parser.add_argument('--include_file', nargs='*', type=str)

    args = parser.parse_args()

    classname = args.classname
    pyclassname = 'Py' + classname
    namespace = args.namespace
    if args.include_file is None:
        include_files = [f'{classname}.h']
    else:
        include_files = args.include_file

    make_header = MkHeader(classname=classname,
                           pyclassname=pyclassname,
                           namespace=namespace,
                           include_files=include_files)
    make_header()
