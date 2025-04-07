#ifndef PYDICT_H
#define PYDICT_H

/// @file PyDict.h
/// @brief PyDict のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2025 Yusuke Matsunaga
/// All rights reserved.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "ym_config.h"


BEGIN_NAMESPACE_YM

//////////////////////////////////////////////////////////////////////
/// @class PyDict PyDict.h "PyDict.h"
/// @brief Python のリストに関する関数を集めたクラス
///
/// - T は要素のクラス
/// - PyT は T と PyObject の間の変換を行うクラス
/// - PyT は PyT::Conv(const T&) と PyT::Deconv(PyObject*, T&)
///   を実装している必要がある．
/// - PyDict 自身もこのインターフェイスを実装している．
//////////////////////////////////////////////////////////////////////
template<class T, class PyT>
class PyDict
{
  using ElemType = std::unordered_map<std::string, T>;

public:

  /// @brief 要素の辞書を表す PyObject* を作るファンクタクラス
  struct Conv {
    PyObject*
    operator()(
      const ElemType& val_dict
    )
    {
      typename PyT::Conv conv;
      auto obj = PyDict_New();
      for ( auto& p: val_dict ) {
	auto key = p.first;
	auto elem = p.second;
	auto elem_obj = conv(elem);
	if ( PyDict_SetItemString(obj, key.c_str(), elem_obj) < 0 ) {
	  return nullptr;
	}
      }
      return obj;
    }

  };


  /// @brief 要素の辞書を取り出すファンクタクラス
  struct Deconv {
    bool
    operator()(
      PyObject* obj,
      ElemType& val_dict
    )
    {
      typename PyT::Deconv deconv;

      if ( !PyDict_Check(obj) ) {
	return false;
      }
      auto items = PyDict_Items(obj);
      auto n = PyList_Size(items);
      val_dict.clear();
      for ( SizeType i = 0; i < n; ++ i ) {
	auto item_obj = PyList_GetItem(items, i);
	const char* key = nullptr;
	PyObject* val_obj = nullptr;
	if ( !PyArg_ParseTuple(item_obj, "sO", &key, &val_obj) ) {
	  return false;
	}
	T val;
	if ( !deconv(val_obj, val) ) {
	  return false;
	}
	val_dict.emplace(key, val);
      }
      Py_DecRef(items);
      return true;
    }
  };


public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief unordered_map<string, T> を表す PyObject を作る．
  /// @return リストを表す Python のオブジェクト(PyDict)を返す．
  static
  PyObject*
  ToPyObject(
    const ElemType& val_dict ///< [in] 値の辞書
  )
  {
    Conv conv;
    return conv(val_dict);
  }

  /// @brief PyObject から unordered_map<string, T> を取り出す．
  /// @return 正しく変換できた時に true を返す．
  ///
  /// deconv は PyObject* から T を取り出すファンクタクラス
  static
  bool
  FromPyObject(
    PyObject* obj,     ///< [in] Python のオブジェクト
    ElemType& val_dict ///< [out] 結果を格納する辞書
  )
  {
    Deconv deconv;
    return deconv(obj, val_dict);
  }

  /// @brief PyObject が辞書型かどうか調べる．
  ///
  /// 要素が T に変換可能かどうかは調べない．
  static
  bool
  Check(
    PyObject* obj ///< [in] 対象の Python オブジェクト
  )
  {
    if ( !PyDict_Check(obj) ) {
      return false;
    }
    auto val_list = PyDict_Values(obj);
    auto n = PyList_Size(val_list);
    bool ans = true;
    for ( SizeType i = 0; i < n; ++ i ) {
      auto val_obj = PyList_GetItem(val_list, i);
      if ( !PyT::Check(val_obj) ) {
	ans = false;
	break;
      }
    }
    Py_DecRef(val_list);
    return ans;
  }

  /// @brief PyObject から std::unordered_map<string, T> を取り出す．
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
    PyErr_SetString(PyExc_TypeError, "not a dictionary type");
    return {};
  }

};

END_NAMESPACE_YM

#endif // PYDICT_H
