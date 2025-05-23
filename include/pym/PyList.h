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
/// @class PyList PyList.h "PyList.h"
/// @brief Python のリストに関する関数を集めたクラス
///
/// - T は要素のクラス
/// - PyT は T と PyObject の間の変換を行うクラス
/// - PyT は PyT::Conv(const T&) と PyT::Deconv(PyObject*, T&)
///   を実装している必要がある．
/// - PyList 自身もこのインターフェイスを実装している．
//////////////////////////////////////////////////////////////////////
template<class T, class PyT>
class PyList
{
public:

  using ElemType = std::vector<T>;

public:

  /// @brief 要素のリストを表す PyObject* を作るファンクタクラス
  struct Conv {
    PyObject*
    operator()(
      const ElemType& val_list
    )
    {
      typename PyT::Conv conv;
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


  /// @brief 要素のリストを取り出すファンクタクラス
  struct Deconv {
    bool
    operator()(
      PyObject* obj,
      ElemType& val_list
    )
    {
      typename PyT::Deconv deconv;

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
	auto ans = deconv(val_obj, val);
	Py_DecRef(val_obj);
	if ( !ans ) {
	  return false;
	}
	val_list.push_back(val);
      }
      return true;
    }
  };


public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief vector<T> を表す PyObject を作る．
  /// @return リストを表す Python のオブジェクト(PyList)を返す．
  static
  PyObject*
  ToPyObject(
    const ElemType& val_list ///< [in] 値のリスト
  )
  {
    Conv conv;
    return conv(val_list);
  }

  /// @brief PyObject から vector<T> を取り出す．
  /// @return 正しく変換できた時に true を返す．
  ///
  /// deconv は PyObject* から T を取り出すファンクタクラス
  static
  bool
  FromPyObject(
    PyObject* obj,     ///< [in] Python のオブジェクト
    ElemType& val_list ///< [out] 結果を格納するリスト
  )
  {
    Deconv deconv;
    return deconv(obj, val_list);
  }

  /// @brief PyObject がシーケンス型かどうか調べる．
  ///
  /// 要素が T に変換可能かどうかは調べない．
  static
  bool
  Check(
    PyObject* obj ///< [in] 対象の Python オブジェクト
  )
  {
    if ( !PySequence_Check(obj) ) {
      return false;
    }
    auto n = PySequence_Size(obj);
    for ( SizeType i = 0; i < n; ++ i ) {
      auto obj1 = PySequence_GetItem(obj, i);
      auto ans = PyT::Check(obj1);
      Py_DecRef(obj1);
      if ( !ans ) {
	return false;
      }
    }
    return true;
  }

  /// @brief PyObject から vector<T> を取り出す．
  static
  ElemType
  Get(
    PyObject* obj ///< [in] 対象の Python オブジェクト
  )
  {
    ElemType val;
    if ( FromPyObject(obj, val) ) {
      return val;
    }
    PyErr_SetString(PyExc_TypeError, "not a sequence type");
    return {};
  }

};

END_NAMESPACE_YM

#endif // PYLIST_H
