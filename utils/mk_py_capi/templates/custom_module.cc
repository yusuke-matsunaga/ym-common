
/// @file %%MODULENAME%%_module.cc
/// @brief Python 用の %%MODULENAME%% モジュールを定義する．
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) %%YEAR%% Yusuke Matsunaga
/// All rights reserved.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

%%INCLUDES%%
#include "pym/PyModule.h"


%%BEGIN_NAMESPACE%%

BEGIN_NONAMESPACE

%%EXTRA_CODE%%
// メソッド定義構造体
PyMethodDef ymbase_methods[] = {
  {nullptr, nullptr, 0, nullptr},
};

// モジュール定義構造体
PyModuleDef %%MODULENAME%%_module = {
  PyModuleDef_HEAD_INIT,
  "%%MODULENAME%%",
  PyDoc_STR("%%DOC_STR%%"),
  -1,
  ymbase_methods,
};

END_NONAMESPACE

PyMODINIT_FUNC
PyInit_%%MODULENAME%%()
{
  auto m = PyModule::init(&%%MODULENAME%%_module);
  if ( m == nullptr ) {
    return nullptr;
  }

  %%INIT_CODE%%

  return m;

 error:
  Py_DECREF(m);
  return nullptr;
}

%%END_NAMESPACE%%
