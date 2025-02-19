#ifndef YM_HEAPTREE_H
#define YM_HEAPTREE_H

/// @file HeapTree.h
/// @brief HeapTree のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2025 Yusuke Matsunaga
/// All rights reserved.

#include "ym_config.h"


BEGIN_NAMESPACE_YM

/// @brief T の比較演算子を用いた比較関数クラス
template<typename T>
struct NaitiveComp
{
  int
  operator()(T a, T b) const
  {
    if ( a < b ) {
      return -1;
    }
    if ( a > b ) {
      return 1;
    }
    return 0;
  }
};


//////////////////////////////////////////////////////////////////////
/// @class HeapTree HeapTree.h "HeapTree.h"
/// @brief ヒープ木を実装するクラス
///
/// 要素の追加と最小要素の取得を O(logN) で実行する．
/// さらにヒープ上にある要素の値の更新と要素の削除も O(logN) で実行する．
///
/// ItemType は通常の整数型を仮定しているが，ハッシュ可能であれば
/// 複合型でも使用可能．
/// CompFuncClass は以下の関数を持つと仮定している．
/// - int CompFuncClass::operator()(ItemType id1,
///                                 ItemType id2) const
///   id1 と id2 の比較結果を返す．
///   負なら id1 が小さい．正なら id2 が小さい．0なら等しい．
//////////////////////////////////////////////////////////////////////
template <typename ItemType = int,
	  typename CompFuncClass = NaitiveComp<ItemType>>
class HeapTree
{
public:

  /// @brief コンストラクタ
  ///
  /// max_size はヒントであり，実際には max_size 以上の
  /// 要素を入れることはできるが，メモリの再確保が起こる
  /// ので効率はよくない．
  HeapTree(
    const CompFuncClass& compare ///< [in] 比較関数
    = CompFuncClass(),
    SizeType max_size = 0        ///< [in] 最大の要素数
  ) : mCompare{compare}
  {
    mArray.reserve(max_size);
  }

  /// @brief デストラクタ
  ~HeapTree() = default;


public:
  //////////////////////////////////////////////////////////////////////
  // 外部インターフェイス
  //////////////////////////////////////////////////////////////////////

  /// @brief ヒープが空の時 true を返す．
  bool
  empty() const
  {
    return mArray.empty();
  }

  /// @brief 要素数を返す．
  SizeType
  size() const
  {
    return mArray.size();
  }

  /// @brief 要素を追加する．
  void
  put_item(
    ItemType item ///< [in] 追加する要素
  )
  {
    if ( heap_pos(item) != 0 ) {
      throw std::invalid_argument{"item has already been in the heap"};
    }

    auto pos = mArray.size();
    mArray.push_back(item);
    mPosMap.emplace(item, pos + 1);
    move_up(item);
  }

  /// @brief 要素を取り去る．
  void
  delete_item(
    ItemType item ///< [in] 削除する要素
  )
  {
    auto pos = heap_pos(item);
    if ( pos == 0 ) {
      throw std::invalid_argument{"item is not in the heap"};
    }

    mPosMap.erase(item);
    auto last = mArray.back();
    mArray.pop_back();
    if ( last != item ) {
      -- pos;
      locate_node(last, pos);
      move_down(last);
    }
  }

  /// @brief 値が最小の要素を取り出す．
  /// その要素はヒープから取り除かれる．
  ItemType
  get_min()
  {
    if ( empty() ) {
      throw std::invalid_argument{"heap is empty"};
    }

    auto item = mArray.front();
    mPosMap.erase(item);
    auto last = mArray.back();
    mArray.pop_back();
    if ( size() > 0 ) {
      locate_node(last, 0);
      move_down(last);
    }
    return item;
  }

  /// @brief 要素の値の変更に伴ってヒープ構造を更新する．
  void
  update(
    ItemType item ///< [in] 値が変更された要素
  )
  {
    auto pos = heap_pos(item);
    if ( pos == 0 ) {
      throw std::invalid_argument{"item is not in the heap"};
    }

    -- pos;
    ASSERT_COND( mArray[pos] == item );

    move_up(item);
    move_down(item);
  }

  /// @brief 要素がヒープに含まれるか調べる．
  bool
  is_in(
    ItemType item ///< [in] 対象の要素
  ) const
  {
    return mPosMap.count(item) > 0;
  }

  /// @brief 内容を出力する．
  void
  print(
    ostream& s ///< [in] 出力先のストリーム
  ) const
  {
    s << " heap_size = " << size() << endl;
    for ( auto item: mArray ) {
      s << " Item#" << heap_pos(item) - 1
	<< ": " << item << endl;
    }
    s << endl;
  }


private:
  //////////////////////////////////////////////////////////////////////
  // 内部で用いられる関数
  //////////////////////////////////////////////////////////////////////

  /// @brief 要素を適当な位置まで沈める．
  void
  move_down(
    ItemType item ///< [in] 対象のノード
  )
  {
    auto pos = heap_pos(item);
    -- pos;
    for ( ; ; ) {
      // ヒープ木の性質から親の位置から子の位置が分かる．
      auto l_pos = pos * 2 + 1;
      auto r_pos = l_pos + 1;
      if ( r_pos > size() ) {
	// 左右の子供を持たない時
	break;
      }
      auto p_item = mArray[pos];
      auto l_item = mArray[l_pos];
      if ( r_pos == size() ) {
	// 右の子供を持たない時
	if ( mCompare(p_item, l_item) > 0 ) {
	  // 逆転
	  locate_node(p_item, l_pos);
	  locate_node(l_item, pos);
	}
	// これ以上子供はいない．
	break;
      }
      else {
	// 左右の子供がいる場合
	auto r_item = mArray[r_pos];
	if ( mCompare(p_item, l_item) > 0 &&
	     mCompare(l_item, r_item) <= 0 ) {
	  // 左の子供と入れ替える．
	  // 次は左の子供に対して同じ事をする．
	  locate_node(p_item, l_pos);
	  locate_node(l_item, pos);
	  pos = l_pos;
	}
	else if ( mCompare(p_item, r_item) > 0 &&
		  mCompare(r_item, l_item) < 0 ) {
	  // 右の子供と入れ替える．
	  // 次は右の子供に対して同じ事をする．
	  locate_node(p_item, r_pos);
	  locate_node(r_item, pos);
	  pos = r_pos;
	}
	else {
	  break;
	}
      }
    }
  }

  /// @brief 要素を適当な位置まで浮かび上がらせる．
  void
  move_up(
    ItemType item ///< [in] 対象の要素
  )
  {
    auto pos = heap_pos(item);
    -- pos;
    while ( pos > 0 ) {
      auto p_pos = (pos - 1) / 2;
      auto p_item = mArray[p_pos];
      if ( mCompare(p_item, item) <= 0 ) {
	break;
      }
      locate_node(item, p_pos);
      locate_node(p_item, pos);
      pos = p_pos;
      item = mArray[pos];
    }
  }

  /// @brief 要素のヒープ上の位置を得る．
  SizeType
  heap_pos(
    ItemType item ///< [in] 要素
  ) const
  {
    if ( mPosMap.count(item) > 0 ) {
      return mPosMap.at(item);
    }
    return 0;
  }

  /// @brief ノードをヒープ上にセットする．
  void
  locate_node(
    ItemType item, ///< [in] 要素
    SizeType pos   ///< [in] 位置
  )
  {
    mArray[pos] = item;
    mPosMap[item] = pos + 1;
  }


private:
  //////////////////////////////////////////////////////////////////////
  // データメンバ
  //////////////////////////////////////////////////////////////////////

  // 要素の配列
  vector<ItemType> mArray;

  // 要素をキーにして mArray 上の位置を持つ辞書
  // 実際には位置＋１の値を持つ．
  std::unordered_map<ItemType, SizeType> mPosMap;

  // 要素の比較用関数オブジェクト
  const CompFuncClass& mCompare;

};

END_NAMESPACE_YM

#endif // YM_HEAPTREE_H
