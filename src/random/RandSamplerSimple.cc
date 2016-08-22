﻿
/// @file RandSamplerSimple.cc
/// @brief RandSamplerSimple の実装ファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2016 Yusuke Matsunaga
/// All rights reserved.


#include "ym/RandSamplerSimple.h"
#include "ym/RandGen.h"


BEGIN_NAMESPACE_YM

// @brief コンストラクタ
// @param[in] weight_array 重みの配列
RandSamplerSimple::RandSamplerSimple(const vector<ymuint>& weight_array)
{
  mNum = static_cast<ymuint>(weight_array.size());
  mAccumArray = new ymuint[mNum + 1];
  ymuint accum = 0;
  for (ymuint i = 0; i < mNum; ++ i) {
    mAccumArray[i] = accum;
    ymuint weight = weight_array[i];
    accum += weight;
  }
  mAccumArray[mNum] = accum;
}

// @brief コンストラクタ
// @param[in] num 要素数
// @param[in] weight_array 重みの配列
RandSamplerSimple::RandSamplerSimple(ymuint num,
				     ymuint weight_array[])
{
  mNum = num;
  mAccumArray = new ymuint[mNum + 1];
  ymuint accum = 0;
  for (ymuint i = 0; i < mNum; ++ i) {
    mAccumArray[i] = accum;
    ymuint weight = weight_array[i];
    accum += weight;
  }
  mAccumArray[mNum] = accum;
}

// @brief デストラクタ
RandSamplerSimple::~RandSamplerSimple()
{
  delete [] mAccumArray;
}

// @brief 要素数を返す．
ymuint
RandSamplerSimple::num() const
{
  return mNum;
}

// @brief 要素の重みを返す．
// @param[in] pos 位置番号 ( 0 <= pos < num() )
ymuint
RandSamplerSimple::weight(ymuint pos) const
{
  ASSERT_COND( pos < num() );

  return mAccumArray[pos + 1] - mAccumArray[pos];
}

// @brief サンプリングを行う．
// @param[in] randgen 乱数発生器
// @return サンプリング結果を返す．
ymuint
RandSamplerSimple::get_sample(RandGen& randgen)
{
  ymuint val = randgen.int32() % mAccumArray[mNum];

  // mAccumArray[i] <= val < mAccumArray[i + 1] --- [1]
  // を満たす i を求める．
  // そのために
  // mAccumArray[left] <= val < mAccumArray[right] --- [2]
  // を満たす left, right を用意する．
  // もちろん left < right
  // で left と right の中点 half = (left + right) / 2
  // をもとめて mAccumArray[half] と val を比較する．
  // mAccumArray[half] <= val なら left を half に置き換える．
  // そうでなければ right を half に置き換える．
  // どちらの置き換えを行っても[2]式の条件は満たされている．
  // left + 1 = right になったとき[1]式が満たされることになるので
  // 繰り返しを終える．
  // アルゴリズムの教科書に載っているような探索アルゴリズム
  ymuint left = 0;
  ymuint right = mNum;
  while ( (left + 1) < right ) {
    ymuint half = (left + right) / 2;
    if ( mAccumArray[half] <= val ) {
      left = half;
    }
    else {
      right = half;
    }
  }
  return left;
}

END_NAMESPACE_YM