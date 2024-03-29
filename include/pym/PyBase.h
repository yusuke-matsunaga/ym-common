#ifndef PYBASE_H
#define PYBASE_H

/// @file PyBase.h
/// @brief PyBase のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2022 Yusuke Matsunaga
/// All rights reserved.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "ym_config.h"


BEGIN_NAMESPACE_YM

//////////////////////////////////////////////////////////////////////
/// @class PyBase PyBase.h "PyBase.h"
/// @brief Python 拡張用の基底クラス
//////////////////////////////////////////////////////////////////////
class PyBase
{
public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief PyObject から文字列を取り出す．
  /// @return 変換が成功したら true を返す．
  ///
  /// 変換が失敗しても Python 例外を設定しない．
  static
  bool
  StringFromPyObject(
    PyObject* obj, ///< [in] 対象のオブジェクト
    string& val    ///< [out] 変換した値を格納するオブジェクト
  )
  {
    if ( PyUnicode_Check(obj) ) {
      auto obj2 = PyUnicode_EncodeLocale(obj, nullptr);
      val = string{PyBytes_AsString(obj2)};
      return true;
    }
    return false;
  }

  /// @brief vector<string> を表す PyObject を作る．
  static
  PyObject*
  ToPyList(
    const vector<string>& val_list ///< [in] 値のリスト
  )
  {
    SizeType n = val_list.size();
    auto obj = PyList_New(n);
    for ( SizeType i = 0; i < n; ++ i ) {
      auto& val = val_list[i];
      auto str_obj = Py_BuildValue("s", val.c_str());
      PyList_SetItem(obj, i, str_obj);
    }
    return obj;
  }

};

END_NAMESPACE_YM

#endif // PYBASE_H
