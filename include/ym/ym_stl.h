#ifndef YM_STL_H
#define YM_STL_H

/// @file ym_stl.h
/// @brief stl 関係のヘッダファイル
/// @author Yusuke Matsunaga (松永 裕介)
///
/// Copyright (C) 2016, 2019 Yusuke Matsunaga
/// All rights reserved.


#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <exception>
#include <new>
#include <utility>
#include <string>
#include <vector>
#include <list>
#include <unordered_set>
#include <unordered_map>
#include <bitset>
#include <regex>
#include <memory>
#include <limits>
#include <utility>
#include <chrono>

#include <algorithm>
#include <functional>

#if 0
//////////////////////////////////////////////////////////////////////
// std:: にある汎用的な名前を自分の名前空間(YM_NAMESPACE)にインポートする
//////////////////////////////////////////////////////////////////////
BEGIN_NAMESPACE_YM

using std::istream;
using std::ifstream;
using std::istringstream;
using std::ostream;
using std::ofstream;
using std::ostringstream;
using std::cin;
using std::cout;
using std::cerr;
using std::endl;
using std::flush;
using std::ios;
using std::setw;
using std::setprecision;
using std::setfill;
using std::hex;
using std::oct;
using std::dec;
using std::fixed;
using std::scientific;
using std::exception;
using std::bad_alloc;
using std::pair;
using std::make_pair;
using std::string;
using std::vector;
using std::list;
using std::unique_ptr;
using std::shared_ptr;
using std::weak_ptr;
using std::initializer_list;
using std::numeric_limits;
using std::unordered_map;
using std::unordered_set;
using std::bitset;
using std::regex;
using std::smatch;
using std::move;
using std::swap;
using std::stoi;
using std::tuple;
using std::make_tuple;
using std::tie;
using std::ignore;

END_NAMESPACE_YM
#endif

#endif // YM_STL_H
