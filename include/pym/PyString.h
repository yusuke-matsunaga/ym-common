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
/// @class PyStringConv PyString.h "PyString.h"
/// @brief string を PyObject* に変換するファンクタクラス
///
/// 実はただの関数
//////////////////////////////////////////////////////////////////////
class PyStringConv
{
public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief string を PyObject* に変換する．
  PyObject*
  operator()(
    const string& val
  )
  {
    return Py_BuildValue("s", val.c_str());
  }

};


//////////////////////////////////////////////////////////////////////
/// @class PyStringCheck PyString.h "PyString.h"
/// @brief string に変換するファンクタクラス
///
/// 実はただの関数
//////////////////////////////////////////////////////////////////////
class PyStringDeconv
{
public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief string に変換する．
  bool
  operator()(
    PyObject* obj,
    string& val
  )
  {
    if ( PyUnicode_Check(obj) ) {
      auto obj2 = PyUnicode_EncodeLocale(obj, nullptr);
      val = string{PyBytes_AsString(obj2)};
      return true;
    }
    return false;
  }

};


//////////////////////////////////////////////////////////////////////
/// @class PyString PyString.h "PyString.h"
/// @brief string の Python 拡張用の基底クラス
//////////////////////////////////////////////////////////////////////
class PyString
{
public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief string を表す PyObject を作る．
  static
  PyObject*
  ToPyObject(
    const string& val
  )
  {
    PyStringConv conv;
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
    string& val    ///< [out] 変換した値を格納するオブジェクト
  )
  {
    PyStringDeconv deconv;
    return deconv(obj, val);
  }

  /// @brief vector<string> を表す PyObject を作る．
  static
  PyObject*
  ToPyList(
    const vector<string>& val_list ///< [in] 値のリスト
  )
  {
    return PyList::ToPyObject<string, PyStringConv>(val_list);
  }

};

END_NAMESPACE_YM

#endif // PYSTRING_H
