
/// @file HeapTreeTest.cc
/// @brief HeapTreeTest の実装ファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2025 Yusuke Matsunaga
/// All rights reserved.

#include <gtest/gtest.h>
#include "ym/HeapTree.h"


BEGIN_NAMESPACE_YM

TEST(HeapTreeTest, int1)
{
  HeapTree<> ht;

  ht.put_item(0);
  ht.put_item(10);
  ht.put_item(5);
  ht.put_item(3);

  EXPECT_EQ( 4, ht.size() );

  EXPECT_EQ( 0, ht.get_min() );
  EXPECT_EQ( 3, ht.get_min() );
  EXPECT_EQ( 5, ht.get_min() );
  EXPECT_EQ( 10, ht.get_min() );
}

TEST(HeapTreeTest, int2)
{
  struct Comp
  {
    int
    operator()(int a, int b) const
    {
      if ( a > b ) {
	return -1;
      }
      if ( a < b ) {
	return 1;
      }
      return 0;
    }
  };

  HeapTree<int, Comp> ht(Comp{});

  ht.put_item(0);
  ht.put_item(10);
  ht.put_item(5);
  ht.put_item(3);

  EXPECT_EQ( 4, ht.size() );

  EXPECT_EQ( 10, ht.get_min() );
  EXPECT_EQ( 5, ht.get_min() );
  EXPECT_EQ( 3, ht.get_min() );
  EXPECT_EQ( 0, ht.get_min() );
}

END_NAMESPACE_YM
