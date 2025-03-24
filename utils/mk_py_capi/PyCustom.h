#ifndef %%PYCUSTOM%%_H
#define %%PYCUSTOM%%_H

/// @file %%PyCustom%%.h
/// @brief %%PyCustom%% のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) %%Year%% Yusuke Matsunaga
/// All rights reserved.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

%%INCLUDES%%


BEGIN_NAMESPACE_%%NAMESPACE%%

//////////////////////////////////////////////////////////////////////
/// @class %%PyCustom%% %%PyCustom%%.h "%%PyCustom%%.h"
/// @brief %%Custom%% を Python から使用するための拡張
///
/// 実際には static メンバ関数しか持たないのでクラスではない．
//////////////////////////////////////////////////////////////////////
class %%PyCustom%%
{
  using ElemType = %%Custom%%;

public:
  %%CONV_DEF%%
  %%DECONV_DEF%%


public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief 初期化する．
  /// @return 初期化が成功したら true を返す．
  static
  bool
  init(
    PyObject* m ///< [in] 親のモジュールを表す PyObject
  );
  %%TOPYOBJECT%%
  %%FROMPYOBJECT%%

  /// @brief PyObject が %%Custom%% タイプか調べる．
  static
  bool
  Check(
    PyObject* obj ///< [in] 対象の PyObject
  );

  /// @brief %%Custom%% を表す PyObject から %%Custom%% を取り出す．
  /// @return %%Custom%% を返す．
  ///
  /// Check(obj) == true であると仮定している．
  static
  ElemType&
  _get_ref(
    PyObject* obj ///< [in] 変換元の PyObject
  );

  /// @brief %%Custom%% を表すオブジェクトの型定義を返す．
  static
  PyTypeObject*
  _typeobject();

};

END_NAMESPACE_%%NAMESPACE%%

#endif // %%PYCUSTOM%%_H
