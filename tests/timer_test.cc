
/// @file timer_test.cc
/// @brief timer_test の実装ファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2022 Yusuke Matsunaga
/// All rights reserved.

#include "ym/Timer.h"
#include <stdlib.h>


BEGIN_NAMESPACE_YM

int
timer_test(
  int argc,
  char** argv
)
{
  Timer timer;

  timer.start();

  // 入力待ち
  getchar();

  timer.stop();

  auto t = timer.get_time();
  std::cout << t << std::endl;

  return 0;
}

END_NAMESPACE_YM


int
main(
  int argc,
  char** argv
)
{
  return YM_NAMESPACE::timer_test(argc, argv);
}
