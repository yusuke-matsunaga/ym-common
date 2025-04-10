#ifndef PYBOOL_H
#define PYBOOL_H

/// @file PyBool.h
/// @brief PyBool のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2025 Yusuke Matsunaga
/// All rights reserved.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "ym_config.h"


BEGIN_NAMESPACE_YM

//////////////////////////////////////////////////////////////////////
/// @class PyBool PyBool.h "PyBool.h"
/// @brief bool と PyObject の間の変換を行うクラス
//////////////////////////////////////////////////////////////////////
class PyBool
{
public:

  using ElemType = bool;

public:

  /// @brief bool を PyObject* に変換するファンクタクラス
  struct Conv {
    PyObject*
    operator()(
      const ElemType& val
    )
    {
      return PyBool_FromLong(val);
    }
  };

  /// @brief PyObject* を bool に変換するファンクタクラス
  struct Deconv {
    bool
    operator()(
      PyObject* obj,
      ElemType& val
    )
    {
      if ( obj == Py_True ) {
	val = true;
	return true;
      }
      if ( obj == Py_False ) {
	val = false;
	return true;
      }
      return false;
    }
  };


public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief string を表す PyObject を作る．
  static
  PyObject*
  ToPyObject(
    const ElemType& val
  )
  {
    Conv conv;
    return conv(val);
  }

  /// @brief PyObject から文字列を取り出す．
  /// @return 変換が成功したら true を返す．
  ///
  /// 変換が失敗しても Python 例外を設定しない．
  static
  bool
  FromPyObject(
    PyObject* obj, ///< [in] 対象のオブジェクト
    ElemType& val  ///< [out] 変換した値を格納するオブジェクト
  )
  {
    Deconv deconv;
    return deconv(obj, val);
  }

  /// @brief PyObject が文字列型か調べる．
  static
  bool
  Check(
    PyObject* obj ///< [in] 対象の PyObject
  )
  {
    return PyBool_Check(obj);
  }

  /// @brief 整数を取り出す．
  ///
  /// Check(obj) == true であると仮定している．
  static
  ElemType
  Get(
    PyObject* obj ///< [in] 対象の PyObject
  )
  {
    if ( obj == Py_True ) {
      return true;
    }
    if ( obj == Py_False ) {
      return false;
    }
    PyErr_SetString(PyExc_TypeError, "Could not convert to 'bool'");
    return false;
  }

};

END_NAMESPACE_YM

#endif // PYBOOL_H
