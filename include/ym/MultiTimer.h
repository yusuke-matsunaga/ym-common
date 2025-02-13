#ifndef MULTITIMER_H
#define MULTITIMER_H

/// @file MultiTimer.h
/// @brief MultiTimer のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2022 Yusuke Matsunaga
/// All rights reserved.

#include "ym_config.h"
#include <chrono>


BEGIN_NAMESPACE_YM

//////////////////////////////////////////////////////////////////////
/// @class MultiTimer MultiTimer.h "MultiTimer.h"
/// @brief 互いに排他的な複数の時区間の計時を行なうクラス
///
/// コンストラクタで時区間の数を指定する．
/// このタイマーでは停止状態はなく，常にいずれかの時区間が計時中
/// となっている．
//////////////////////////////////////////////////////////////////////
template<class ClockType>
class MultiTimer_
{
  using time_point = typename ClockType::time_point;
  using duration = std::chrono::duration<double, std::milli>;

public:

  /// @brief コンストラクタ
  MultiTimer_(
    SizeType num ///< [in] 時区間の数 ( > 0 )
  ) : mAccTime(num, 0.0)
  {
    start(0);
  }

  /// @brief デストラクタ
  ~MultiTimer_() = default;


public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief 時区間の数を返す．
  SizeType
  num() const
  {
    return mAccTime.size();
  }

  /// @brief すべての累積経過時間をリセットする．
  void
  reset_all()
  {
    for ( int i = 0; i < num(); ++ i ) {
      mAccTime[i] = 0.0;
    }
  }

  /// @brief 指定された時区間の経過時間をリセットする．
  void
  reset(
    SizeType id ///< [in] 時区間の番号 ( 0 <= id < num() )
  )
  {
    _check_id(id);
    mAccTime[id] = 0.0;
  }

  /// @brief 指定された時区間の計時を開始する．
  void
  start(
    SizeType id ///< [in] 時区間の番号 ( 0 <= id < num() )
  )
  {
    _check_id(id);
    if ( id != mCurId ) {
      stop();
      mCurId = id;
      mStartTime = ClockType::now();
    }
  }

  /// @brief 指定された時区間の累積経過時間(ミリ秒)を返す．
  double
  get_time(
    SizeType id ///< [in] 時区間の番号 ( 0 <= id < num() )
  ) const
  {
    _check_id(id);
    return mAccTime[id];
  }


private:
  //////////////////////////////////////////////////////////////////////
  // 内部で用いられる関数
  //////////////////////////////////////////////////////////////////////

  /// @brief 現在計時中の時区間の計時を停止する．
  void
  stop()
  {
    duration d = ClockType::now() - mStartTime;
    mAccTime[mCurId] += d.count();
  }

  /// @brief id が適正な値かチェックする．
  void
  _check_id(
    SizeType id
  ) const
  {
    if ( id >= num() ) {
      throw std::out_of_range{"id is out of range"};
    }
  }


private:
  //////////////////////////////////////////////////////////////////////
  // データメンバ
  //////////////////////////////////////////////////////////////////////

  // 現在計時中の時区間番号
  SizeType mCurId{0};

  // 計時開始時刻
  time_point mStartTime;

  // 累積経過時間(ミリ秒)
  vector<double> mAccTime;

};

using MultiTimer = MultiTimer_<std::chrono::steady_clock>;

END_NAMESPACE_YM

#endif // MULTITIMER_H
