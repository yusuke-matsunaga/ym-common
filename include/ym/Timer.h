#ifndef TIMER_H
#define TIMER_H

/// @file Timer.h
/// @brief Timer のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2022 Yusuke Matsunaga
/// All rights reserved.

#include "ym_config.h"
#include <chrono>


BEGIN_NAMESPACE_YM

//////////////////////////////////////////////////////////////////////
/// @class Timer Timer.h "Timer.h"
/// @brief 時間計測を行なうクラス
///
/// タイマーは以下の2つの状態を持つ．
/// - 停止中
/// - 計時中
///
/// start() で 停止中 -> 計時中 に遷移する．
/// stop() で 計時中 -> 停止中 に遷移する．
/// それ以外の組み合わせでは状態はあ変更されない．
///
/// get_time() で計時中の累積経過時間を返す．
/// reset() で累積経過時間をリセットする．
//////////////////////////////////////////////////////////////////////
template<class ClockType>
class Timer_
{
  using time_point = typename ClockType::time_point;
  using duration = std::chrono::duration<double, std::milli>;

public:

  /// @brief コンストラクタ
  Timer_() = default;

  /// @brief デストラクタ
  ~Timer_() = default;


public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief リセットする．
  ///
  /// 計時中の場合には停止中になる．
  void
  reset()
  {
    stop();
    mAccTime = 0.0;
  }

  /// @brief 計時を開始する．
  void
  start()
  {
    if ( !mRunning ) {
      mRunning = true;
      mStartTime = ClockType::now();
    }
  }

  /// @brief 計時を停止する．
  void
  stop()
  {
    if ( mRunning ) {
      mRunning = false;
      duration d = ClockType::now() - mStartTime;
      mAccTime += d.count();
    }
  }

  /// @brief 累積経過時間(ミリ秒)を返す．
  double
  get_time() const
  {
    return mAccTime;
  }


private:
  //////////////////////////////////////////////////////////////////////
  // データメンバ
  //////////////////////////////////////////////////////////////////////

  // 計時中の時 true となるフラグ
  bool mRunning{false};

  // 計時開始時刻
  time_point mStartTime;

  // 累積経過時間(ミリ秒)
  double mAccTime{0.0};

};

/// @brief steady_clock を用いたタイマーの定義
using Timer = Timer_<std::chrono::steady_clock>;

END_NAMESPACE_YM

#endif // TIMER_H
