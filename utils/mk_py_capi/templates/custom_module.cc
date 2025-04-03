
/// @file %%ModuleName%%_module.cc
/// @brief Python 用の %%ModuleName%% モジュールを定義する．
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) %%Year%% Yusuke Matsunaga
/// All rights reserved.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

%%INCLUDES%%
#include "pym/PyModule.h"


%%BEGIN_NAMESPACE%%

BEGIN_NONAMESPACE
%%EXTRA_CODE%%

// モジュール定義構造体
PyModuleDef %%ModuleName%%_module = {
  PyModuleDef_HEAD_INIT,
  "%%ModuleName%%",
  PyDoc_STR("%%DOC_STR%%"),
  -1,
  methods,
};

END_NONAMESPACE

PyMODINIT_FUNC
PyInit_%%ModuleName%%()
{
  auto m = PyModule::init(&%%ModuleName%%_module);
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
