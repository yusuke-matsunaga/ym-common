
/// @file MultiTimerTest.cc
/// @brief MultiTimerTest の実装ファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2022 Yusuke Matsunaga
/// All rights reserved.

#include "ym/MultiTimer.h"


BEGIN_NAMESPACE_YM

void
multitimer_test()
{
  MultiTimer mt(3);

  mt.start(1);
  double d = 0.0;
  for ( int i = 0; i < 1000 * 1000; ++ i ) {
    d += sin(i * 3.1415);
  }
  mt.start(2);
  d = 0.0;
  for ( int i = 0; i < 1000 * 1000; ++ i ) {
    for ( int j = 0; j < 100; ++ j ) {
      d += cos(i * 3.1415);
    }
  }
  mt.start(0);
  cout << mt.get_time(0) << endl
       << mt.get_time(1) << endl
       << mt.get_time(2) << endl;
}

END_NAMESPACE_YM


int
main(
  int argc,
  char** argv
)
{
  YM_NAMESPACE::multitimer_test();
  return 0;
}
