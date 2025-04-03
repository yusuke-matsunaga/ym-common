#ifndef PYM_%%CapModuleName%%_H
#define PYM_%%CapModuleName%%_H

/// @file %%ModuleName%%.h
/// @brief %%ModuleName%% の初期化関数のエクスポート
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) %%Year%% Yusuke Matsunaga
/// All rights reserved.

#include "ym_config.h"


%%BEGIN_NAMESPACE%%

/// @brief %%ModuleName%% モジュールの初期化関数
extern "C" PyObject* PyInit_%%ModuleName%%();

%%END_NAMESPACE%%

#endif // PYM_%%CapModuleName%%_H
