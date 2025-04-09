#ifndef PYINT_H
#define PYINT_H

/// @file PyInt.h
/// @brief PyInt のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2025 Yusuke Matsunaga
/// All rights reserved.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "ym_config.h"


BEGIN_NAMESPACE_YM

//////////////////////////////////////////////////////////////////////
/// @class PyInt PyInt.h "PyInt.h"
/// @brief int と PyObject の間の変換を行うクラス
///
/// PyLong_XXX 関数のラッパクラス
//////////////////////////////////////////////////////////////////////
class PyInt
{
public:

  using ElemType = int;

public:

  /// @brief string を PyObject* に変換するファンクタクラス
  struct Conv {
    PyObject*
    operator()(
      const ElemType& val
    )
    {
      return PyLong_FromLong(val);
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
      if ( PyInt::Check(obj) ) {
	val = PyInt::Get(obj);
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

  /// @brief PyObject から整数を取り出す．
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

  /// @brief PyObject が整数型か調べる．
  static
  bool
  Check(
    PyObject* obj ///< [in] 対象の PyObject
  )
  {
    return PyLong_Check(obj);
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
    return static_cast<int>(PyLong_AsLong(obj));
  }

};

END_NAMESPACE_YM

#endif // PYINT_H
