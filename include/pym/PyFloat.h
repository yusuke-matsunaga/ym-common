#ifndef PYFLOAT_H
#define PYFLOAT_H

/// @file PyFloat.h
/// @brief PyFloat のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2025 Yusuke Matsunaga
/// All rights reserved.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "ym_config.h"


BEGIN_NAMESPACE_YM

//////////////////////////////////////////////////////////////////////
/// @class PyFloat PyFloat.h "PyFloat.h"
/// @brief double と PyObject の間の変換を行うクラス
///
/// PyFloat_XXX 関数のラッパクラス
//////////////////////////////////////////////////////////////////////
class PyFloat
{
  using ElemType = double;

public:

  /// @brief string を PyObject* に変換するファンクタクラス
  struct Conv {
    PyObject*
    operator()(
      const ElemType& val
    )
    {
      return PyFloat_FromDouble(val);
    }
  };

  /// @brief PyObject* を string に変換するファンクタクラス
  struct Deconv {
    bool
    operator()(
      PyObject* obj,
      ElemType& val
    )
    {
      if ( PyFloat::Check(obj) ) {
	val = PyFloat::Get(obj);
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
    return PyFloat_Check(obj);
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
    return PyFloat_AsDouble(obj);
  }

};

END_NAMESPACE_YM

#endif // PYFLOAT_H
