#ifndef PYLIST_H
#define PYLIST_H

/// @file PyList.h
/// @brief PyList のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2025 Yusuke Matsunaga
/// All rights reserved.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "ym_config.h"


BEGIN_NAMESPACE_YM

//////////////////////////////////////////////////////////////////////
/// @class PyListConv PyList.h "PyList.h"
/// @brief 要素のリストを表す PyObject* を作るファンクタクラス
///
/// - T は要素のクラス
/// - Conv は T を PyObject に変換するファンクタクラス
//////////////////////////////////////////////////////////////////////
template<class T, class Conv>
class PyListConv
{
public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief 要素のリストを表す PyObject* を作る．
  PyObject*
  operator()(
    const std::vector<T>& val_list
  )
  {
    Conv conv;
    SizeType n = val_list.size();
    auto obj = PyList_New(n);
    for ( SizeType i = 0; i < n; ++ i ) {
      auto& val = val_list[i];
      auto val_obj = conv(val);
      PyList_SET_ITEM(obj, i, val_obj);
    }
    return obj;
  }

};


//////////////////////////////////////////////////////////////////////
/// @class PyListDeconv PyList.h "PyList.h"
/// @brief 要素のリストを取り出すファンクタクラス
///
/// - T は要素のクラス
/// - Deconv は PyObject* を T に変換するファンクタクラス
//////////////////////////////////////////////////////////////////////
template<class T, class Deconv>
class PyListDeconv
{
public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief 要素のリストを取り出す．
  bool
  operator()(
    PyObject* obj,
    std::vector<T>& val_list
  )
  {
    Deconv deconv;

    // 特例: obj が T そのものだった場合．
    {
      T val;
      if ( deconv(obj, val) ) {
	val_list = {val};
	return true;
      }
    }

    // 通常は T を表す PyObject のシーケンス
    if ( !PySequence_Check(obj) ) {
      return false;
    }
    auto n = PySequence_Size(obj);
    val_list.clear();
    val_list.reserve(n);
    for ( SizeType i = 0; i < n; ++ i ) {
      auto val_obj = PySequence_GetItem(obj, i);
      T val;
      if ( !deconv(val_obj, val) ) {
	return false;
      }
      val_list.push_back(val);
    }
    return true;
  }

};


//////////////////////////////////////////////////////////////////////
/// @class PyList PyList.h "PyList.h"
/// @brief Python のリストに関する関数を集めたクラス
//////////////////////////////////////////////////////////////////////
class PyList
{
public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief vector<T> を表す PyObject を作る．
  /// @return リストを表す Python のオブジェクト(PyList)を返す．
  ///
  /// conv は T を PyObject* に変換するファンクタクラス
  template<class T, class Conv>
  static
  PyObject*
  ToPyObject(
    const vector<T>& val_list ///< [in] 値のリスト
  )
  {
    PyListConv<T, Conv> conv;
    return conv(val_list);
  }

  /// @brief PyObject から vector<T> を取り出す．
  /// @return 正しく変換できた時に true を返す．
  ///
  /// deconv は PyObject* から T を取り出すファンクタクラス
  template<class T, class Deconv>
  static
  bool
  FromPyObject(
    PyObject* obj,           ///< [in] Python のオブジェクト
    std::vector<T>& val_list ///< [out] 結果を格納するリスト
  )
  {
    PyListDeconv<T, Deconv> deconv;
    return deconv(obj, val_list);
  }

};

END_NAMESPACE_YM

#endif // PYLIST_H
