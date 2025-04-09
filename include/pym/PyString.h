#ifndef PYSTRING_H
#define PYSTRING_H

/// @file PyString.h
/// @brief PyString のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2022 Yusuke Matsunaga
/// All rights reserved.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "ym_config.h"
#include "pym/PyList.h"


BEGIN_NAMESPACE_YM

//////////////////////////////////////////////////////////////////////
/// @class PyString PyString.h "PyString.h"
/// @brief string と PyObject の間の変換を行うクラス
//////////////////////////////////////////////////////////////////////
class PyString
{
public:

  using ElemType = string;

public:

  /// @brief string を PyObject* に変換するファンクタクラス
  struct Conv {
    PyObject*
    operator()(
      const ElemType& val
    )
    {
      return Py_BuildValue("s", val.c_str());
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
      if ( PyString::Check(obj) ) {
	val = PyString::Get(obj);
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

  /// @brief vector<string> を表す PyObject を作る．
  static
  PyObject*
  ToPyList(
    const vector<ElemType>& val_list ///< [in] 値のリスト
  )
  {
    return PyList<ElemType, PyString>::ToPyObject(val_list);
  }

  /// @brief PyObject が文字列型か調べる．
  static
  bool
  Check(
    PyObject* obj ///< [in] 対象の PyObject
  )
  {
    return PyUnicode_Check(obj);
  }

  /// @brief 文字列を取り出す．
  ///
  /// Check(obj) == true であると仮定している．
  static
  std::string
  Get(
    PyObject* obj ///< [in] 対象の PyObject
  )
  {
    auto obj2 = PyUnicode_EncodeLocale(obj, nullptr);
    return std::string{PyBytes_AsString(obj2)};
  }

};

END_NAMESPACE_YM

#endif // PYSTRING_H
