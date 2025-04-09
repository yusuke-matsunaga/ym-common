
/// @file %%PyCustom%%.cc
/// @brief %%PyCustom%% の実装ファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) %%Year%% Yusuke Matsunaga
/// All rights reserved.

%%INCLUDES%%
#include "pym/PyModule.h"


%%BEGIN_NAMESPACE%%

BEGIN_NONAMESPACE

// Python 用のオブジェクト定義
// この構造体は同じサイズのヒープから作られるので
// mVal のコンストラクタは起動されないことに注意．
// そのためあとでコンストラクタを明示的に起動する必要がある．
// またメモリを開放するときにも明示的にデストラクタを起動する必要がある．
struct %%CustomObject%%
{
  PyObject_HEAD
  %%Custom%% mVal;
};

// Python 用のタイプ定義
PyTypeObject %%CustomType%% = {
  PyVarObject_HEAD_INIT(nullptr, 0)
  // 残りは %%PyCustom%%::init() 中で初期化する．
};
%%EXTRA_CODE%%

END_NONAMESPACE


// @brief %%TypeName%% オブジェクトを使用可能にする．
bool
%%PyCustom%%::init(
  PyObject* m
)
{
  %%TP_INIT_CODE%%
  if ( !PyModule::reg_type(m, "%%TypeName%%", &%%CustomType%%) ) {
    goto error;
  }
  %%EX_INIT_CODE%%

  return true;

 error:

  return false;
}
%%CONV_CODE%%

// @brief PyObject が %%Custom%% タイプか調べる．
bool
%%PyCustom%%::Check(
  PyObject* obj
)
{
  return Py_IS_TYPE(obj, &%%CustomType%%);
}

// @brief PyObject から %%Custom%% を取り出す．
%%Custom%%&
%%PyCustom%%::_get_ref(
  PyObject* obj
)
{
  auto my_obj = reinterpret_cast<%%CustomObject%%*>(obj);
  return my_obj->mVal;
}

// @brief %%Custom%% を表すオブジェクトの型定義を返す．
PyTypeObject*
%%PyCustom%%::_typeobject()
{
  return &%%CustomType%%;
}

%%END_NAMESPACE%%
