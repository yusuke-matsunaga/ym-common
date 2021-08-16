#ifndef YM_ASSERT_H
#define YM_ASSERT_H

/// @file ym_assert.h
/// @brief assertion 関係のクラス
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2016, 2021 Yusuke Matsunaga
/// All rights reserved.


BEGIN_NAMESPACE_YM

//////////////////////////////////////////////////////////////////////
/// @brief assertion チェック用の変数(定数)
//////////////////////////////////////////////////////////////////////
#ifdef NDEBUG
const bool ym_check = false;
#else
// NDEBUG に関わらずチェックを行いたくなければ
// この値を false にすればよい．
const bool ym_check = true;
#endif


//////////////////////////////////////////////////////////////////////
/// @class AssertError ym_assert.h "ym_assert.h"
/// @brief assert 違反用の例外の基底クラス
///
/// このクラスは例外が起こったファイル名と行番号を持つ．
//////////////////////////////////////////////////////////////////////
class AssertError :
  public exception
{
public:

  /// @brief コンストラクタ
  AssertError(
    const char* file,
    int line
  ) : mFileName(file),  ///< [in] ファイル名
      mLineNumber(line) ///< [in] 行番号
  {
  }


public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief assert 違反の発生したソースファイル名
  const char*
  file_name() const { return mFileName; }

  /// @brief assert 違反の発生したソースファイルの行番号
  int
  line_number() const { return mLineNumber; }


private:
  //////////////////////////////////////////////////////////////////////
  // データメンバ
  //////////////////////////////////////////////////////////////////////

  // ファイル名
  const char* mFileName;

  // 行番号
  int mLineNumber;

};


//////////////////////////////////////////////////////////////////////
/// @relates AssertError
/// @brief AssertError を ostream に書き出す
/// @return s をそのまま返す
//////////////////////////////////////////////////////////////////////
inline
ostream&
operator<<(
  ostream& s,            ///< [in] 出力ストリーム
  const AssertError& obj ///< [in] エラーオブジェクト
)
{
  s << "assertion failed at file: " << obj.file_name()
    << ", line: " << obj.line_number();
  return s;
}


//////////////////////////////////////////////////////////////////////
/// @class AssertNotReached ym_assert.h "ym_assert.h"
/// @brief 到達してはいけない部分に達したときの例外クラス
//////////////////////////////////////////////////////////////////////
class AssertNotReached :
  public AssertError
{
public:
  /// @brief コンストラクタ
  ///
  /// 通常 file, line には __FILE__, __LINE__ マクロを用いる．
  AssertNotReached(
    const char* file, ///< [in] ファイル名
    int line          ///< [in] 行番号
  ) : AssertError(file, line) { }
};


//////////////////////////////////////////////////////////////////////
/// @relates AssertNotReached
/// @brief 通常は到達してはいけない部分に達したときに例外を投げる関数．
///
/// 通常 file, line には __FILE__, __LINE__ マクロを用いる．
//////////////////////////////////////////////////////////////////////
inline
void
assert_not_reached(
  const char* file, ///< [in] 例外の発生したソースファイル名
  int line          ///< [in] 例外の発生したソースファイルの行番号
)
{
  if ( ym_check ) throw AssertNotReached(file, line);
}


//////////////////////////////////////////////////////////////////////
/// @brief assert 違反で任意の例外クラスを投げるテンプレート関数
//////////////////////////////////////////////////////////////////////
template<typename A,
	 typename E>
void
assert_cond(
  A assertion, ///< [in] 例外発生条件
  E except     ///< [in] エラーオブジェクト
)
{
  if ( ym_check && !assertion ) throw except;
}


//////////////////////////////////////////////////////////////////////
/// @relates AssertError
/// @brief assert 違反で AssertError 例外を投げるテンプレート関数
///
/// 通常 file, line には __FILE__, __LINE__ マクロを用いる．
//////////////////////////////////////////////////////////////////////
template<typename A>
void
assert_cond(
  A assertion,      ///< [in] 例外発生条件
  const char* file, ///< [in] ファイル名
  int line          ///< [in] 行番号
)
{
  if ( ym_check && !assertion ) throw AssertError(file, line);
}


//////////////////////////////////////////////////////////////////////
/// @relates AssertNotReached
/// @brief 通常は到達してはいけない部分に達したときに例外を投げるマクロ
///
/// ソースプログラム中で
/// @code{.cpp}
///   ...
///   ASSERT_NOT_REACHED;
/// @endcode
/// という風に使う．ここに実行が到達したら例外が送出される．
//////////////////////////////////////////////////////////////////////
#define ASSERT_NOT_REACHED assert_not_reached(__FILE__, __LINE__)


//////////////////////////////////////////////////////////////////////
/// @relates AssertError
/// @brief assert 違反で AssertError 例外を投げるマクロ
/// @param[in] assertion 例外発生条件
///
/// ソースプログラム中で
/// @code{.cpp}
///   ...
///   ASSERT_COND( x > 0 );
/// @endcode
/// という風に使う．この例では x > 0 が成り立たないと例外が送出される．
//////////////////////////////////////////////////////////////////////
#define ASSERT_COND(assertion) assert_cond(assertion, __FILE__, __LINE__)

END_NAMESPACE_YM

#endif // YM_ASSERT_H
