#ifndef PYINT32_H
#define PYINT32_H

/// @file PyInt32.h
/// @brief PyInt32 のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2025 Yusuke Matsunaga
/// All rights reserved.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "ym_config.h"


BEGIN_NAMESPACE_YM

//////////////////////////////////////////////////////////////////////
/// @class PyInt32 PyInt32.h "PyInt32.h"
/// @brief std::int32_t と PyObject の間の変換を行うクラス
///
/// PyLong_XXX 関数のラッパクラス
//////////////////////////////////////////////////////////////////////
class PyInt32
{
public:

  using ElemType = std::int32_t;

public:

  /// @brief std::int32_t を PyObject* に変換するファンクタクラス
  struct Conv {
    PyObject*
    operator()(
      const ElemType& val
    )
    {
      return PyLong_FromLong(val);
    }
  };

  /// @brief PyObject* を std::int32_t に変換するファンクタクラス
  struct Deconv {
    bool
    operator()(
      PyObject* obj,
      ElemType& val
    )
    {
      if ( PyInt32::Check(obj) ) {
	val = PyInt32::Get(obj);
	return true;
      }
      return false;
    }
  };


public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief std::int32_t を表す PyObject を作る．
  static
  PyObject*
  ToPyObject(
    const ElemType& val
  )
  {
    Conv conv;
    return conv(val);
  }

  /// @brief PyObject から値を取り出す．
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
    return PyLong_AsLong(obj);
  }

};

END_NAMESPACE_YM

#endif // PYINT32_H
