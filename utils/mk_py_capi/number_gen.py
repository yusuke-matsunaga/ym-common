#! /usr/bin/env python3

""" NumberGen のクラス定義ファイル

:file: number_gen.py
:author: Yusuke Matsunaga (松永 裕介)
:copyright: Copyright (C) 2025 Yusuke Matsunaga, All rights reserved.
"""

from .funcgen import FuncBase, CArg
from .utils import gen_func, add_member_def


class OpBase:
    """演算の情報を表すクラス
    """

    def __init__(self, classname, *,
                 useref=True):
        self.__classname = classname
        self.__useref = useref

    def __call__(self, writer, *,
                 retclassname,
                 objname,
                 varname):
        with writer.gen_if_block(f'{self.__classname}::Check({objname})'):
            if self.__useref:
                writer.gen_autoref_assign(varname,
                                          f'{self.__classname}::_get_ref({objname})')
            else:
                writer.gen_auto_assign(varname,
                                       f'{self.__classname}::Get({objname})')
            self.body(writer, retclassname)


class Op(OpBase):

    def __init__(self, classname, expr, *,
                 useref=True):
        super().__init__(classname=classname, useref=useref)
        self.__expr = expr

    def body(self, writer, retclassname):
        writer.gen_return_pyobject(retclassname, self.__expr)


class AddOp(Op):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         expr='val1 + val2',
                         useref=useref)


class SubOp(Op):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         expr='val1 - val2',
                         useref=useref)


class MulOp(Op):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         expr='val1 * val2',
                         useref=useref)


class DivOp(Op):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         expr='val1 / val2',
                         useref=useref)


class RemOp(Op):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         expr='val1 % val2',
                         useref=useref)


class LsftOp(Op):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         expr='val1 << val2',
                         useref=useref)


class RsftOp(Op):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         expr='val1 >> val2',
                         useref=useref)


class AndOp(Op):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         expr='val1 & val2',
                         useref=useref)


class XorOp(Op):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         expr='val1 ^ val2',
                         useref=useref)


class OrOp(Op):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         expr='val1 | val2',
                         useref=useref)


class Iop(OpBase):

    def __init__(self, classname, stmt, *,
                 useref=True):
        super().__init__(classname=classname, useref=useref)
        self.__stmt = stmt

    def body(self, writer, _):
        writer.write_line(f'{self.__stmt};')
        writer.gen_return_self(incref=True)


class AddIop(Iop):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         stmt='val1 += val2',
                         useref=useref)


class SubIop(Iop):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         stmt='val1 -= val2',
                         useref=useref)


class MulIop(Iop):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         stmt='val1 *= val2',
                         useref=useref)


class DivIop(Iop):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         stmt='val1 /= val2',
                         useref=useref)


class RemIop(Iop):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         stmt='val1 %= val2',
                         useref=useref)


class LsftIop(Iop):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         stmt='val1 <<= val2',
                         useref=useref)


class RsftIop(Iop):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         stmt='val1 >>= val2',
                         useref=useref)


class AndIop(Iop):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         stmt='val1 &= val2',
                         useref=useref)


class XorIop(Iop):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         stmt='val1 &= val2',
                         useref=useref)


class XorIop(Iop):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         stmt='val1 ^= val2',
                         useref=useref)


class OrIop(Iop):

    def __init__(self, classname, *,
                 useref=True):
        super().__init__(classname=classname,
                         stmt='val1 |= val2',
                         useref=useref)


class BinOpGen(FuncBase):
    """二項演算を生成するクラス
    """

    def __init__(self, gen, name, *,
                 op_list1,
                 op_list2=[]):
        def body(writer):
            c0 = gen.pyclassname
            with writer.gen_if_block(f'{c0}::Check(self)'):
                writer.gen_autoref_assign('val1', f'{c0}::_get_ref(self)')
                for op in op_list1:
                    op(writer,
                       retclassname=c0,
                       objname='other',
                       varname='val2')
            if len(op_list2) > 0:
                with writer.gen_if_block(f'{c0}::Check(other)'):
                    writer.gen_autoref_assign('val2', f'{c0}::_get_ref(other)')
                    for op in op_list2:
                        op(writer,
                           retclassname=c0,
                           objname='self',
                           varname='val1')
            writer.gen_return_py_notimplemented()
        super().__init__(gen, name, None, body)

    def __call__(self, writer, *,
                 comment=None,
                 comments=None):
        args = [CArg.Self(),
                CArg.Other()]
        with writer.gen_func_block(comment=comment,
                                   comments=comments,
                                   return_type='PyObject*',
                                   func_name=self.name,
                                   args=args):
            with writer.gen_try_block():
                self.body(writer)
            writer.gen_catch_invalid_argument()


class NumberGen:
    """Number オブジェクト構造体を作るクラス
    """

    def __init__(self, gen, name):
        self.__gen = gen
        self.name = name
        self.pyclassname = gen.pyclassname
        self.nb_add=None
        self.nb_subtract=None
        self.nb_multiply=None
        self.nb_remainder=None
        self.nb_divmod=None
        self.nb_power=None
        self.nb_negative=None
        self.nb_positive=None
        self.nb_absolute=None
        self.nb_bool=None
        self.nb_invert=None
        self.nb_lshift=None
        self.nb_rshift=None
        self.nb_and=None
        self.nb_xor=None
        self.nb_or=None
        self.nb_int=None
        self.nb_float=None
        self.nb_inplace_add=None
        self.nb_inplace_subtract=None
        self.nb_inplace_multiply=None
        self.nb_inplace_remainder=None
        self.nb_inplace_power=None
        self.nb_inplace_lshift=None
        self.nb_inplace_rshift=None
        self.nb_inplace_and=None
        self.nb_inplace_xor=None
        self.nb_inplace_or=None
        self.nb_floor_divide=None
        self.nb_true_divide=None
        self.nb_inplace_floor_divide=None
        self.nb_inplace_true_divide=None
        self.nb_index=None
        self.nb_matrix_multiply=None
        self.nb_inplace_matrix_multiply=None

    def add_add(self, func_name, *,
                expr='default',
                op_list1=[],
                op_list2=[]):
        if self.nb_add is not None:
            raise ValueError('nb_add has been already defined')
        if expr is not None:
            if expr == 'default':
                op = AddOp(self.pyclassname)
            else:
                op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_add = BinOpGen(self, func_name,
                               op_list1=op_list1,
                               op_list2=op_list2)

    def add_subtract(self, func_name, *,
                     expr='default',
                     op_list1=[],
                     op_list2=[]):
        if self.nb_subtract is not None:
            raise ValueError('nb_subtract has been already defined')
        if expr is not None:
            if expr == 'default':
                op = SubOp(self.pyclassname)
            else:
                op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_subtract = BinOpGen(self, func_name,
                                    op_list1=op_list1,
                                    op_list2=op_list2)

    def add_multiply(self, func_name, *,
                     expr='default',
                     op_list1=[],
                     op_list2=[]):
        if self.nb_multiply is not None:
            raise ValueError('nb_multiply has been already defined')
        if expr is not None:
            if expr == 'default':
                op = MulOp(self.pyclassname)
            else:
                op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_multiply = BinOpGen(self, func_name,
                                    op_list1=op_list1,
                                    op_list2=op_list2)

    def add_remainder(self, func_name, *,
                      expr='default',
                      op_list1=[],
                      op_list2=[]):
        if self.nb_remainder is not None:
            raise ValueError('nb_remainder has been already defined')
        if expr is not None:
            if expr == 'default':
                op = RemOp(self.pyclassname)
            else:
                op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_remainder = BinOpGen(self, func_name,
                                     op_list1=op_list1,
                                     op_list2=op_list2)

    def add_divmod(self, func_name, *,
                   expr=None,
                   op_list1=[],
                   op_list2=[]):
        if self.nb_divmod is not None:
            raise ValueError('nb_divmod has been already defined')
        if expr is not None:
            op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_divmod = BinOpGen(self, func_name,
                                  op_list1=op_list1,
                                  op_list2=op_list2)

    def add_power(self, body):
        if self.nb_power is not None:
            raise ValueError('nb_power has been already defined')
        self.nb_power = body

    def add_negative(self, body):
        if self.nb_negative is not None:
            raise ValueError('nb_negative has been already defined')
        self.nb_negative = body

    def add_positive(self, body):
        if self.nb_positive is not None:
            raise ValueError('nb_positive has been already defined')
        self.nb_positive = body

    def add_absolute(self, body):
        if self.nb_absolute is not None:
            raise ValueError('nb_absolute has been already defined')
        self.nb_absolute = body

    def add_bool(self, body):
        if self.nb_bool is not None:
            raise ValueError('nb_bool has been already defined')
        self.nb_bool = body

    def add_invert(self, body):
        if self.nb_invert is not None:
            raise ValueError('nb_invert has been already defined')
        self.nb_invert = body

    def add_lshift(self, func_name, *,
                   expr='default',
                   op_list1=[]):
        if self.nb_lshift is not None:
            raise ValueError('nb_lshift has been already defined')
        if expr is not None:
            if expr == 'default':
                op = LsftOp(self.pyclassname)
            else:
                op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_lshift = BinOpGen(self, func_name,
                                  op_list1=op_list1)

    def add_rshift(self, func_name, *,
                   expr='default',
                   op_list1=[]):
        if self.nb_rshift is not None:
            raise ValueError('nb_rshift has been already defined')
        if expr is not None:
            if expr == 'default':
                op = RsftOp(self.pyclassname)
            else:
                op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_rshift = BinOpGen(self, func_name,
                                  op_list1=op_list1)

    def add_and(self, func_name, *,
                expr='default',
                op_list1=[],
                op_list2=[]):
        if self.nb_and is not None:
            raise ValueError('nb_and has been already defined')
        if expr is not None:
            if expr == 'default':
                op = AndOp(self.pyclassname)
            else:
                op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_and = BinOpGen(self, func_name,
                               op_list1=op_list1,
                               op_list2=op_list2)

    def add_xor(self, func_name, *,
                expr='default',
                op_list1=[],
                op_list2=[]):
        if self.nb_xor is not None:
            raise ValueError('nb_xor has been already defined')
        if expr is not None:
            if expr == 'default':
                op = XorOp(self.pyclassname)
            else:
                op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_xor = BinOpGen(self, func_name,
                               op_list1=op_list1,
                               op_list2=op_list2)

    def add_or(self, func_name, *,
               expr='default',
               op_list1=[],
               op_list2=[]):
        if self.nb_or is not None:
            raise ValueError('nb_or has been already defined')
        if expr is not None:
            if expr == 'default':
                op = OrOp(self.pyclassname)
            else:
                op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_or = BinOpGen(self, func_name,
                              op_list1=op_list1,
                              op_list2=op_list2)

    def add_int(self, body):
        if self.nb_int is not None:
            raise ValueError('nb_int has been already defined')
        self.nb_int = body

    def add_float(self, body):
        if self.nb_float is not None:
            raise ValueError('nb_float has been already defined')
        self.nb_float = body

    def add_inplace_add(self, func_name, *,
                        stmt='default',
                        op_list1=[]):
        if self.nb_inplace_add is not None:
            raise ValueError('nb_inplace_add has been already defined')
        if stmt is not None:
            if stmt == 'default':
                op = AddIop(self.pyclassname)
            else:
                op = Iop(self.pyclassname, stmt)
            op_list1 = [op] + op_list1
        self.nb_inplace_add = BinOpGen(self, func_name,
                                       op_list1=op_list1)

    def add_inplace_subtract(self, func_name, *,
                             stmt='default',
                             op_list1=[]):
        if self.nb_inplace_subtract is not None:
            raise ValueError('nb_inplace_subtract has been already defined')
        if stmt is not None:
            if stmt == 'default':
                op = SubIop(self.pyclassname)
            else:
                op = Iop(self.pyclassname, stmt)
            op_list1 = [op] + op_list1
        self.nb_inplace_subtract = BinOpGen(self, func_name,
                                            op_list1=op_list1)

    def add_inplace_multiply(self, func_name, *,
                             stmt='default',
                             op_list1=[]):
        if self.nb_inplace_multiply is not None:
            raise ValueError('nb_inplace_multiply has been already defined')
        if stmt is not None:
            if stmt == 'default':
                op = MulIop(self.pyclassname)
            else:
                op = Iop(self.pyclassname, stmt)
            op_list1 = [op] + op_list1
        self.nb_inplace_multiply = BinOpGen(self, func_name,
                                            op_list1=op_list1)

    def add_inplace_remainder(self, func_name, *,
                              stmt='default',
                              op_list1=[]):
        if self.nb_inplace_remainder is not None:
            raise ValueError('nb_inplace_remainder has been already defined')
        if stmt is not None:
            if stmt == 'default':
                op = RemIop(self.pyclassname)
            else:
                op = Iop(self.pyclassname, stmt)
            op_list1 = [op] + op_list1
        self.nb_inplace_remainder = BinOpGen(self, func_name,
                                             op_list1=op_list1)

    def add_inplace_power(self, body):
        if self.nb_inplace_power is not None:
            raise ValueError('nb_inplace_power has been already defined')
        self.nb_inplace_power = body

    def add_inplace_lshift(self, func_name, *,
                           stmt='default',
                           op_list1=[]):
        if self.nb_inplace_lshift is not None:
            raise ValueError('nb_inplace_lshift has been already defined')
        if stmt is not None:
            if stmt == 'default':
                op = LsftIop(self.pyclassname)
            else:
                op = Iop(self.pyclassname, stmt)
            op_list1 = [op] + op_list1
        self.nb_inplace_lshift = BinOpGen(self, func_name,
                                          op_list1=op_list1)

    def add_inplace_rshift(self, func_name, *,
                           stmt='default',
                           op_list1=[]):
        if self.nb_inplace_rshift is not None:
            raise ValueError('nb_inplace_rshift has been already defined')
        if stmt is not None:
            if stmt == 'default':
                op = RsftIop(self.pyclassname)
            else:
                op = Iop(self.pyclassname, stmt)
            op_list1 = [op] + op_list1
        self.nb_inplace_rshift = BinOpGen(self, func_name,
                                          op_list1=op_list1)

    def add_inplace_and(self, func_name, *,
                        stmt='default',
                        op_list1=[]):
        if self.nb_inplace_and is not None:
            raise ValueError('nb_inplace_and has been already defined')
        if stmt is not None:
            if stmt == 'default':
                op = AndIop(self.pyclassname)
            else:
                op = Iop(self.pyclassname, stmt)
            op_list1 = [op] + op_list1
        self.nb_inplace_and = BinOpGen(self, func_name,
                                       op_list1=op_list1)

    def add_inplace_xor(self, func_name, *,
                        stmt='default',
                        op_list1=[]):
        if self.nb_inplace_xor is not None:
            raise ValueError('nb_inplace_xor has been already defined')
        if stmt is not None:
            if stmt == 'default':
                op = XorIop(self.pyclassname)
            else:
                op = Iop(self.pyclassname, stmt)
            op_list1 = [op] + op_list1
        self.nb_inplace_xor = BinOpGen(self, func_name,
                                       op_list1=op_list1)

    def add_inplace_or(self, func_name, *,
                       stmt='default',
                       op_list1=[]):
        if self.nb_inplace_or is not None:
            raise ValueError('nb_inplace_or has been already defined')
        if stmt is not None:
            if stmt == 'default':
                op = OrIop(self.pyclassname)
            else:
                op = Iop(self.pyclassname, stmt)
            op_list1 = [op] + op_list1
        self.nb_inplace_or = BinOpGen(self, func_name,
                                      op_list1=op_list1)

    def add_floor_divide(self, func_name, *,
                         expr=None,
                         op_list1=[],
                         op_list2=[]):
        if self.nb_floor_divide is not None:
            raise ValueError('nb_floor_divide has been already defined')
        if expr is not None:
            op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_floor_divide = BinOpGen(self, func_name,
                                        op_list1=op_list1,
                                        op_list2=op_list2)

    def add_true_divide(self, func_name, *,
                        expr='default',
                        op_list1=[],
                        op_list2=[]):
        if self.nb_true_divide is not None:
            raise ValueError('nb_divide has been already defined')
        if expr is not None:
            if expr == 'default':
                op = DivOp(self.pyclassname)
            else:
                op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_true_divide = BinOpGen(self, func_name,
                                       op_list1=op_list1,
                                       op_list2=op_list2)

    def add_inplace_floor_divide(self, func_name, *,
                                 stmt=None,
                                 op_list1=[]):
        if self.nb_inplace_floor_divide is not None:
            raise ValueError('nb_inplace_floor_divide has been already defined')
        if stmt is not None:
            op = Iop(self.pyclassname, stmt)
            op_list1 = [op] + op_list1
        self.nb_inplace_floor_divide = BinOpGen(self, func_name,
                                                op_list1=op_list1)

    def add_inplace_true_divide(self, func_name, *,
                                stmt=None,
                                op_list1=[]):
        if self.nb_inplace_true_divide is not None:
            raise ValueError('nb_inplace_true_divide has been already defined')
        if stmt is not None:
            if stmt == 'default':
                op = DivIop(self.pyclassname)
            else:
                op = Iop(self.pyclassname, stmt)
            op_list1 = [op] + op_list1
        self.nb_inplace_true_divide = BinOpGen(self, func_name,
                                               op_list1=op_list1)

    def add_index(self, body):
        if self.nb_index is not None:
            raise ValueError('nb_index has been already defined')
        self.nb_index = body

    def add_matrix_multiply(self, func_name, *,
                            expr=None,
                            op_list1=[],
                            op_list2=[]):
        if self.nb_matrix_multiply is not None:
            raise ValueError('nb_matrix_multiply has been already defined')
        if expr is not None:
            op = Op(self.pyclassname, expr)
            op_list1 = [op] + op_list1
        self.nb_matrix_multiply = BinOpGen(self, func_name,
                                           op_list1=op_list1,
                                           op_list2=op_list2)

    def add_inplace_matrix_multiply(self, func_name, *,
                                    stmt=None,
                                    op_list1=[]):
        if self.nb_inplace_matrix_multiply is not None:
            raise ValueError('nb_inplace_matrix_multiply has been already defined')
        if stmt is not None:
            op = Iop(self.pyclassname, stmt)
            op_list1 = [op] + op_list1
        self.nb_inplace_matrix_multiply = BinOpGen(self, func_name,
                                                   op_list1=op_list1)


    def __call__(self, writer):
        # 個々の関数を生成する．
        gen_func(self.nb_add, writer)
        gen_func(self.nb_subtract, writer)
        gen_func(self.nb_multiply, writer)
        gen_func(self.nb_remainder, writer)
        gen_func(self.nb_divmod, writer)
        gen_func(self.nb_power, writer)
        gen_func(self.nb_negative, writer)
        gen_func(self.nb_positive, writer)
        gen_func(self.nb_absolute, writer)
        gen_func(self.nb_bool, writer)
        gen_func(self.nb_invert, writer)
        gen_func(self.nb_lshift, writer)
        gen_func(self.nb_rshift, writer)
        gen_func(self.nb_and, writer)
        gen_func(self.nb_xor, writer)
        gen_func(self.nb_or, writer)
        gen_func(self.nb_int, writer)
        gen_func(self.nb_float, writer)
        gen_func(self.nb_inplace_add, writer)
        gen_func(self.nb_inplace_subtract, writer)
        gen_func(self.nb_inplace_multiply, writer)
        gen_func(self.nb_inplace_remainder, writer)
        gen_func(self.nb_inplace_power, writer)
        gen_func(self.nb_inplace_lshift, writer)
        gen_func(self.nb_inplace_rshift, writer)
        gen_func(self.nb_inplace_and, writer)
        gen_func(self.nb_inplace_xor, writer)
        gen_func(self.nb_inplace_or, writer)
        gen_func(self.nb_floor_divide, writer)
        gen_func(self.nb_true_divide, writer)
        gen_func(self.nb_inplace_floor_divide, writer)
        gen_func(self.nb_inplace_true_divide, writer)
        gen_func(self.nb_index, writer)
        gen_func(self.nb_matrix_multiply,writer)
        gen_func(self.nb_inplace_matrix_multiply, writer)

        # 構造体定義を生成する．
        with writer.gen_struct_init_block(structname='PyNumberMethods',
                                          varname=self.name,
                                          comment='Numberオブジェクト構造体'):
            nb_lines = []
            add_member_def(nb_lines, 'nb_add', self.nb_add)
            add_member_def(nb_lines, 'nb_subtract', self.nb_subtract)
            add_member_def(nb_lines, 'nb_multiply', self.nb_multiply)
            add_member_def(nb_lines, 'nb_remainder', self.nb_remainder)
            add_member_def(nb_lines, 'nb_divmod', self.nb_divmod)
            add_member_def(nb_lines, 'nb_power', self.nb_power)
            add_member_def(nb_lines, 'nb_negative', self.nb_negative)
            add_member_def(nb_lines, 'nb_positive', self.nb_positive)
            add_member_def(nb_lines, 'nb_absolute', self.nb_absolute)
            add_member_def(nb_lines, 'nb_bool', self.nb_bool)
            add_member_def(nb_lines, 'nb_invert', self.nb_invert)
            add_member_def(nb_lines, 'nb_lshift', self.nb_lshift)
            add_member_def(nb_lines, 'nb_rshift', self.nb_rshift)
            add_member_def(nb_lines, 'nb_and', self.nb_and)
            add_member_def(nb_lines, 'nb_xor', self.nb_xor)
            add_member_def(nb_lines, 'nb_or', self.nb_or)
            add_member_def(nb_lines, 'nb_int', self.nb_int)
            add_member_def(nb_lines, 'nb_float', self.nb_float)
            add_member_def(nb_lines, 'nb_inplace_add', self.nb_inplace_add)
            add_member_def(nb_lines, 'nb_inplace_subtract', self.nb_inplace_subtract)
            add_member_def(nb_lines, 'nb_inplace_multiply', self.nb_inplace_multiply)
            add_member_def(nb_lines, 'nb_inplace_remainder', self.nb_inplace_remainder)
            add_member_def(nb_lines, 'nb_inplace_power', self.nb_inplace_power)
            add_member_def(nb_lines, 'nb_inplace_lshift', self.nb_inplace_lshift)
            add_member_def(nb_lines, 'nb_inplace_rshift', self.nb_inplace_rshift)
            add_member_def(nb_lines, 'nb_inplace_and', self.nb_inplace_and)
            add_member_def(nb_lines, 'nb_inplace_xor', self.nb_inplace_xor)
            add_member_def(nb_lines, 'nb_inplace_or', self.nb_inplace_or)
            add_member_def(nb_lines, 'nb_floor_divide', self.nb_floor_divide)
            add_member_def(nb_lines, 'nb_true_divide', self.nb_true_divide)
            add_member_def(nb_lines, 'nb_inplace_floor_divide',
                           self.nb_inplace_floor_divide)
            add_member_def(nb_lines, 'nb_inplace_true_divide',
                           self.nb_inplace_true_divide)
            add_member_def(nb_lines, 'nb_index', self.nb_index)
            add_member_def(nb_lines, 'nb_matrix_multiply', self.nb_matrix_multiply)
            add_member_def(nb_lines, 'nb_inplace_matrix_multiply',
                           self.nb_inplace_matrix_multiply)
            writer.write_lines(nb_lines, delim=',')

    def gen_tp(self, writer):
        writer.gen_assign(f'{self.__gen.typename}.tp_as_number',
                          f'&{self.name}')
