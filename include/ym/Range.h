#ifndef RANGE_H
#define RANGE_H

/// @file Range.h
/// @brief Range のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2018, 2021 Yusuke Matsunaga
/// All rights reserved.


#include "ym_config.h"


BEGIN_NAMESPACE_YM

//////////////////////////////////////////////////////////////////////
/// @class RangeIterator Range.h "Range.h"
/// @brief Range 用の反復子
//////////////////////////////////////////////////////////////////////
template<class T, int step = 1>
class RangeIterator
{
public:

  /// @brief コンストラクタ
  RangeIterator(
    T pos /// [in] 現在の値
  ) : mCurPos{pos}
  {
  }

  /// @brief デストラクタ
  ~RangeIterator() = default;


public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief dereference 演算子
  T
  operator*() const
  {
    return mCurPos;
  }

  /// @brief increment 演算子
  const RangeIterator&
  operator++()
  {
    mCurPos += step;

    return *this;
  }

  /// @brief 等価比較演算子
  bool
  operator==(
    const RangeIterator& right ///< [in] オペランド
  ) const
  {
    return mCurPos == right.mCurPos;
  }

  /// @brief 非等価比較演算子
  bool
  operator!=(
    const RangeIterator& right ///< [in] オペランド
  ) const
  {
    return !operator==(right);
  }


private:
  //////////////////////////////////////////////////////////////////////
  // データメンバ
  //////////////////////////////////////////////////////////////////////

  // 現在の位置
  T mCurPos;

};


//////////////////////////////////////////////////////////////////////
/// @class Range Range.h "Range.h"
/// @brief c++11 の for 文で用いる範囲を生成するクラス
///
/// Python の range() とほぼおなじ機能
//////////////////////////////////////////////////////////////////////
template<class T, int step = 1>
class Range_
{
public:
  using iterator = RangeIterator<T, step>;

  /// @brief コンストラクタ
  ///
  /// @code
  /// for ( auto i: Range<int, step>(start, end) ) {
  ///   ...
  /// }
  /// @endcoe
  /// のように用いる．これは
  /// @code
  /// for ( int i = start; i < end; i += step ) {
  ///   ...
  /// }
  /// @endcode
  /// と同義になる．
  /// ただし step が負の時には i > end が継続条件になる．
  ///
  /// start < end かつ step < 0 の場合などは無限ループになる．
  Range_(
    T start, ///< [in] 開始位置
    T end    ///< [in] 終了位置
  ) : mStart{start},
      mEnd{end}
  {
    // sanity check
    if ( mStart < mEnd ) {
      ASSERT_COND( step > 0 );
    }
    else if ( mStart > mEnd ) {
      ASSERT_COND( step < 0 );
    }

    // 終了位置の補正を行う．
    if ( ((mEnd - mStart) % step) != 0 ) {
      mEnd = (((mEnd - mStart) / step) + 1) * step + mStart;
    }
  }

  /// @brief 開始位置を省略したコンストラクタ
  ///
  /// start = 0 とする．
  explicit
  Range_(
    T end ///< [in] 終了位置
  ) : mStart{0},
      mEnd{end}
  {
  }

  /// @brief デストラクタ
  ~Range_() = default;


public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief 開始位置の反復子を返す．
  iterator
  begin() const
  {
    return iterator(mStart);
  }

  /// @brief 終了位置の反復子を返す．
  iterator
  end() const
  {
    return iterator(mEnd);
  }


private:
  //////////////////////////////////////////////////////////////////////
  // データメンバ
  //////////////////////////////////////////////////////////////////////

  // 開始位置
  T mStart;

  // 終了位置
  T mEnd;

};

/// @brief Range_<int, 1> の別名
using Range = Range_<int, 1>;

END_NAMESPACE_YM

#endif // RANGE_H
