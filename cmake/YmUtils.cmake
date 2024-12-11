# いくつかのマクロ，関数を集めたファイル

# ym_init: ym-common の初期化を行うマクロ
#
# 入力: "USE_BZIP2" bzip2 を使うとき指定する．
#       "USE_LZMA"  lzma を使うとき指定する．
#       "USE_ZLIB"  gzip を使うとき指定する．
#       "USE_POPT"  popt を使うとき指定する．
#
# 出力: YM_UNIX     unix 系のプラットフォームの時セットされる．
#       YM_APPLE    mac 系のプラットフォームの時セットされる．
#       YM_WIN32    windows 系のプラットフォームの時セットされる．
#       BZIP2_FOUND bzip2 が使用可能の時セットされる．
#       LZMA_FOUND  lzma が使用可能の時セットされる．
#       ZLIB_FOUND  gzip が使用可能の時セットされる．
#       POPT_FOUND  popt が使用可能の時セットされる．
#
#       YM_LIB_DEPENDS bzip2, lzma, gzip, popt などの依存するライブラリ
macro ( ym_init )

  # bzip2 ライブラリを使う．
  set ( __USE_BZIP2 OFF )

  # LZMA ライブラリを使う．
  set ( __USE_LZMA OFF )

  # gzip ライブラリを使う．
  set ( __USE_ZLIB OFF )

  # popt ライブラリを使う．
  set ( __USE_POPT OFF )

  foreach ( __arg ${ARGV} )
    if ( ${__arg} STREQUAL USE_BZIP2 )
      set ( __USE_BZIP2 ON )
    elseif ( ${__arg} STREQUAL USE_LZMA )
      set ( __USE_LZMA ON )
    elseif ( ${__arg} STREQUAL USE_ZLIB )
      set ( __USE_ZLIB ON )
    elseif ( ${__arg} STREQUAL USE_POPT )
      set ( __USE_POPT ON )
    else ()
      # エラー
      message ( FATAL_ERROR "illegal argument in ym_init(): " ${__arg} )
    endif ()
  endforeach ()

  # ===================================================================
  # システムの検査
  # ===================================================================

  if ( UNIX )
    set ( YM_UNIX 1 )
  endif ( UNIX )
  if ( APPLE )
    set ( YM_APPLE 1 )
  endif ( APPLE )
  if ( WIN32 )
    set ( YM_WIN32 1 )
  endif ( WIN32 )


  # ===================================================================
  # パッケージの検査
  # ===================================================================

  if ( __USE_BZIP2 )
    include (FindBZip2)
  endif ()

  if ( __USE_LZMA )
    include (FindLibLZMA)
  endif ()

  if ( __USE_ZLIB )
    include (FindZLIB)
  endif ()

  if ( __USE_POPT )
    include (FindPOPT)
  endif ()


  # ===================================================================
  # インクルードディレクトリの設定
  # ===================================================================

  if ( ZLIB_FOUND )
    include_directories(${ZLIBINCLUDE_DIRS})
  endif ( ZLIB_FOUND )

  if ( BZIP2_FOUND )
    include_directories(${BZIP2_INCLUDE_DIRS})
  endif ( BZIP2_FOUND )

  if ( LIBLZMA_FOUND )
    include_directories(${LIBLZMA_INCLUDE_DIRS})
  endif ( LIBLZMA_FOUND )

  if ( POPT_FOUND )
    include_directories(${POPT_INCLUDE_DIR})
  endif ( POPT_FOUND )


  # ===================================================================
  # リンクすべきライブラリの設定
  # ===================================================================

  set ( YM_LIB_DEPENDS -pthread )

  if ( ZLIB_FOUND )
    list (APPEND YM_LIB_DEPENDS ${ZLIB_LIBRARIES})
  endif ( ZLIB_FOUND )

  if ( BZIP2_FOUND )
    list (APPEND YM_LIB_DEPENDS ${BZIP2_LIBRARIES})
  endif ( BZIP2_FOUND )

  if ( LIBLZMA_FOUND )
    list (APPEND YM_LIB_DEPENDS ${LIBLZMA_LIBRARIES})
  endif ( LIBLZMA_FOUND )

  if ( POPT_FOUND )
    list (APPEND YM_LIB_DEPENDS ${POPT_LIBRARY})
  endif ( POPT_FOUND )

endmacro ()


# Python3 に関する初期化を行う．
#
# 入力: なし
# 出力: PYTHON_INTERP Python の実行ファイル
#       PYTHON_VERSION_MAJOR Python の major バージョン
#       PYTHON_VERSION_MINOR Python の minor バージョン
#       ... FindPythonInterp, FindPythonLibs によって設定される変数
#       YM_PYTHON_STRING: Python3.6 のような文字列
#       YM_PYTHON_LIBDIR: ここで生成される Python ライブラリの格納先
macro ( ym_init_python )
  # Python のバージョン指定
  find_package( Python3 ${ARGV} COMPONENTS Interpreter Development )

  set( YM_PYTHON_STRING "python${Python3_VERSION_MAJOR}.${Python3_VERSION_MINOR}" )
  set( YM_PYTHON_LIBDIR "lib/${YM_PYTHON_STRING}/site-packages/" )
endmacro ()

# Cython に関する初期化を行う．
#
# 入力: なし
# 出力: CYTHON_EXECUTABLE cython のプログラム
#       ... FindCython で定義される変数
macro ( ym_init_cython )
  include ( UseCython )
endmacro ()

# Doxygen に関する初期化を行う．
macro ( ym_init_doxygen )
  include ( FindDoxygen )
endmacro ()

# Lua に関する初期化を行う．
#
# 入力: なし
# 出力: LUA_FOUND:          Lua が見つかった時 true
#       LUA_LIBRARIES:      lualib のパス
#       LUA_INCLUDE_DIR:    lua.h のパス
#       LUA_VERSION_STRING: バージョン文字列
#       LUA_VERSION_MAJOR:  メイジャーバージョン
#       LUA_VERSION_MINOR:  マイナーバージョン
#       LUA_VERSION_PATCH:  パッチレベル
macro ( ym_init_lua )
  include ( FindLua )
endmacro ()

# Jsoncpp に関する初期化を行う．
#
# 入力: なし
# 出力: JsonCpp_FOUND: jsoncpp が見つかった時 true
#       JsonCpp_INCLUDE_DIR: jsoncpp のインクルードパス
#       JsonCpp_LIBRARY: jsoncpp のライブラリ
#       JsonCpp::JsonCpp ライブラリターゲット
macro ( ym_init_jsoncpp )
  include ( FindJsoncpp )
  if ( ${JsonCpp_FOUND} )
    include_directories ( ${JsonCpp_INCLUDE_DIR} )
    list ( APPEND YM_LIB_DEPENDS ${JsonCpp_LIBRARY} )
  endif ()
endmacro ()

# Curses に関する初期化を行う．
#
# 入力: なし
# 出力: CURSES_FOUND
#       CURSES_INCLUDE_DIRS
#       CURSES_LIBRAIRES
#       CURSES_CFLAGS
#       CURSES_HAVE_CURSES_H
#       CURSES_HAVE_NCURSES_H
#       CURSES_HAVE_NCURSES_NCURSES_H
#       CURSES_HAVE_NCURSES_CURSES_H
macro ( ym_init_curses )
  include ( FindCurses )
endmacro ()

# Readline に関する初期化を行う．
#
# 入力: なし
# 出力: Readline_FOUND
#       Readline_INCLUDE_DIRS
#       Readline_LIBRARY
macro ( ym_init_readline )
  include ( FindReadline )
endmacro ()

# Curl に関する初期化を行う．
#
# 入力: なし
# 出力: CURL_FOUND:          curl が見つかった時 true
#       CURL_INCLUDE_DIRS:   インクルードディレクトリ
#       CURL_LIBRARIES:      ライブラリ
#       CURL_VERSION_STRING: バージョンを表す文字列
macro ( ym_init_curl )
  include ( FindCURL )
endmacro ()

# Google PerfTools に関する初期化を行う．
macro ( ym_init_gperftools )
  find_package ( Gperftools )
endmacro ()

# CTest に関する初期化を行う．
macro ( ym_init_ctest )
  include ( CTest )
  enable_testing ()
endmacro ()

# libevent を使うためのマクロ
# 入力: なし
# 出力: LIBEVENT_FOUND:       libevent が見つかった時 true
#       LIBEVENT_INCLUDE_DIR: インクルードディレクトリ
#       LIBEVENT_LIBRARIES:   ライブラリ
macro ( ym_init_libevent )
  include ( FindLibevent )
endmacro ()

# curlpp を使うためのマクロ
# 入力: なし
# 出力: CURLPP_FOUND:       curlpp が見つかった時 true
#       CURLPP_INCLUDE_DIR: インクルードディレクトリ
#       CURLPP_LIBRARIES:   ライブラリ
macro ( ym_init_curlpp )
  include ( FindCURLpp )
endmacro ()

# libevent を使うためのマクロ
# 入力: なし
# 出力: LIBEVENT_FOUND:       libevent が見つかった時 true
#       LIBEVENT_INCLUDE_DIR: インクルードディレクトリ
#       LIBEVENT_LIBRARIES:   ライブラリ
macro ( ym_init_libevent )
  include ( FindLibEvent )
endmacro ()

# ym_use_gtest: googletest を使うためのマクロ
#
# 入力: GIT_REPOSITORY       gtest の git レポジトリ(オプション)
#       GIT_TAG              gtest の git タグ(オプション)
# 出力: GTEST_INCLUDE_DIRS   gtest 用のインクルードディレクトリ
#       GTEST_LIBRARY        gtest ライブラリ
#       GTEST_MAIN_LIBRARY   gtest_main ライブラリ
#       GTEST_BOTH_LIBRARIES gtest 用のライブラリ
function ( ym_use_gtest )
  include(ExternalProject)
  find_package(Threads REQUIRED)

  set( __git_repository https://github.com/google/googletest.git )
  set( __git_tag release-1.11.0 )
  if ( ${ARGC} )
    math( EXPR __n "${ARGC} - 1" )
    foreach ( pos RANGE 0 ${__n} )
      list ( GET ARGV ${pos} __arg )
      if ( ${__arg} STREQUAL GIT_REPOSITORY )
	math ( EXPR pos1 "${pos} + 1")
	list ( GET ARGV ${pos1} __val )
	set ( __git_repository ${__val} )
	set ( pos ${pos1} )
      elseif ( ${__arg} STREQUAL GIT_TAG )
	math ( EXPR pos1 "${pos} + 1")
	list ( GET ARGV ${pos1} __val )
	set ( __git_tag ${__val} )
	set ( pos ${pos1} )
      endif ()
    endforeach ()
  endif ()

  ExternalProject_Add(
    googletest
    GIT_REPOSITORY ${__git_repository}
    GIT_TAG ${__git_tag}
    UPDATE_COMMAND ""
    INSTALL_COMMAND ""
    LOG_DOWNLOAD ON
    LOG_CONFIGURE ON
    LOG_BUILD ON
    # ninja の dependency バグを回避するためのコード
    # はっきりいって美しくない
    BUILD_BYPRODUCTS
    ${CMAKE_CURRENT_BINARY_DIR}/googletest-prefix/src/googletest-build/lib/libgtest.a
    ${CMAKE_CURRENT_BINARY_DIR}/googletest-prefix/src/googletest-build/lib/libgtest_main.a
    ${CMAKE_CURRENT_BINARY_DIR}/googletest-prefix/src/googletest-build/lib/libgmock.a
    ${CMAKE_CURRENT_BINARY_DIR}/googletest-prefix/src/googletest-build/lib/libgmock_main.a
    )

  ExternalProject_Get_Property(googletest source_dir)
  set(GTEST_INCLUDE_DIRS ${source_dir}/googletest/include PARENT_SCOPE)
  set(GMOCK_INCLUDE_DIRS ${source_dir}/googlemock/include PARENT_SCOPE)

  ExternalProject_Get_Property(googletest binary_dir)
  set(GTEST_LIBRARY_PATH ${binary_dir}/lib/${CMAKE_FIND_LIBRARY_PREFIXES}gtest.a)
  set(GTEST_LIBRARY_PATH ${GTEST_LIBRARY_PATH} PARENT_SCOPE)
  set(GTEST_LIBRARY gtest)
  set(GTEST_LIBRARY ${GTEST_LIBRARY} PARENT_SCOPE)
  add_library(${GTEST_LIBRARY} UNKNOWN IMPORTED)
  set_target_properties(${GTEST_LIBRARY} PROPERTIES
    IMPORTED_LOCATION ${GTEST_LIBRARY_PATH})
  if ( ${CMAKE_THREAD_LIBS_INIT} )
    set_target_properties(${GTEST_LIBRARY} PROPERTIES
      IMPORTED_LINK_INTERFACE_LIBRARIES ${CMAKE_THREAD_LIBS_INIT})
  endif ()
  add_dependencies(${GTEST_LIBRARY} googletest)

  set(GTEST_MAIN_LIBRARY_PATH ${binary_dir}/lib/${CMAKE_FIND_LIBRARY_PREFIXES}gtest_main.a)
  set(GTEST_MAIN_LIBRARY_PATH ${GTEST_MAIN_LIBRARY_PATH} PARENT_SCOPE)
  set(GTEST_MAIN_LIBRARY gtest_main)
  set(GTEST_MAIN_LIBRARY ${GTEST_MAIN_LIBRARY} PARENT_SCOPE)
  add_library(${GTEST_MAIN_LIBRARY} UNKNOWN IMPORTED)
  set_target_properties(${GTEST_MAIN_LIBRARY} PROPERTIES
    IMPORTED_LOCATION ${GTEST_MAIN_LIBRARY_PATH})
  if ( ${CMAKE_THREAD_LIBS_INIT} )
    set_target_properties(${GTEST_LIBRARY} PROPERTIES
      IMPORTED_LINK_INTERFACE_LIBRARIES ${CMAKE_THREAD_LIBS_INIT})
  endif ()
  add_dependencies(${GTEST_MAIN_LIBRARY} googletest)

  set(GTEST_BOTH_LIBRARIES ${GTEST_LIBRARY} ${GTEST_MAIN_LIBRARY} PARENT_SCOPE)

  set(GMOCK_LIBRARY_PATH ${binary_dir}/lib/${CMAKE_FIND_LIBRARY_PREFIXES}gmock.a)
  set(GMOCK_LIBRARY_PATH ${GMOCK_LIBRARY_PATH} PARENT_SCOPE)
  set(GMOCK_LIBRARY gmock)
  set(GMOCK_LIBRARY ${GMOCK_LIBRARY} PARENT_SCOPE)
  add_library(${GMOCK_LIBRARY} UNKNOWN IMPORTED)
  set_target_properties(${GMOCK_LIBRARY} PROPERTIES
    IMPORTED_LOCATION ${GMOCK_LIBRARY_PATH}
    )
  if ( ${CMAKE_THREAD_LIBS_INIT} )
    set_target_properties(${GTEST_LIBRARY} PROPERTIES
      IMPORTED_LINK_INTERFACE_LIBRARIES ${CMAKE_THREAD_LIBS_INIT})
  endif ()
  add_dependencies(${GMOCK_LIBRARY} googletest)

  set(GMOCK_MAIN_LIBRARY_PATH ${binary_dir}/lib/${CMAKE_FIND_LIBRARY_PREFIXES}gmock_main.a)
  set(GMOCK_MAIN_LIBRARY_PATH ${GMOCK_MAIN_LIBRARY} PARENT_SCOPE)
  set(GMOCK_MAIN_LIBRARY gmock_main)
  set(GMOCK_MAIN_LIBRARY ${GMOCK_MAIN_LIBRARY} PARENT_SCOPE)
  add_library(${GMOCK_MAIN_LIBRARY} UNKNOWN IMPORTED)
  set_target_properties(${GMOCK_MAIN_LIBRARY} PROPERTIES
    IMPORTED_LOCATION ${GMOCK_MAIN_LIBRARY_PATH}
    )
  if ( ${CMAKE_THREAD_LIBS_INIT} )
    set_target_properties(${GTEST_LIBRARY} PROPERTIES
      IMPORTED_LINK_INTERFACE_LIBRARIES ${CMAKE_THREAD_LIBS_INIT})
  endif ()
  add_dependencies(${GMOCK_MAIN_LIBRARY} ${GTEST_LIBRARY})

endfunction ()

# ym_init_submodules: サブモジュール関係の変数を設定するマクロ
#
# 入力: サブモジュール名(ディレクトリ名)のリスト
# 出力: YM_SUBMODULE_LIST サブモジュール名のリスト
#       YM_SUBMODULE_INCLUDE_DIRS サブモジュールのインクルードディレクトリのリスト
#       YM_SUBMODULE_CYTHON_DIRS サブモジュールの Cython ディレクトリのリスト
#       YM_SUBMODULE_OBJ_LIST サブモジュールのオブジェクトのリスト
#       YM_SUBMODULE_OBJ_D_LIST サブモジュールの debug 版オブジェクトのリスト
#       YM_SUBMODULE_OBJ_P_LIST サブモジュールの gperf 版オブジェクトのリスト
macro ( ym_init_submodules )
  set ( YM_SUBMODULE_LIST )
  set ( YM_SUBMODULE_INCLUDE_LIST )
  set ( YM_SUBMODULE_CYTHON_LIST )
  set ( YM_SUBMODULE_OBJ_LIST )
  set ( YM_SUBMODULE_OBJ_D_LIST )
  set ( YM_SUBMODULE_OBJ_P_LIST )
  foreach ( __arg ${ARGV} )
    list ( APPEND YM_SUBMODULE_LIST "${__arg}" )
    list ( APPEND YM_SUBMODULE_INCLUDE_LIST "${PROJECT_SOURCE_DIR}/${__arg}/include" )
    if ( ${__arg} STREQUAL "ym-common" )
      continue ()
    endif ()
    list ( APPEND YM_SUBMODULE_CYTHON_LIST "${PROJECT_SOURCE_DIR}/${__arg}/cython-src" )
    string ( REPLACE "-" "_" __obj ${__arg} )
    list ( APPEND YM_SUBMODULE_OBJ_LIST "$<TARGET_OBJECTS:${__obj}_obj>" )
    list ( APPEND YM_SUBMODULE_OBJ_D_LIST "$<TARGET_OBJECTS:${__obj}_obj_d>" )
    list ( APPEND YM_SUBMODULE_OBJ_P_LIST "$<TARGET_OBJECTS:${__obj}_obj_p>" )
  endforeach ()
endmacro ()

# ヘッダファイルを生成するためのマクロ
#
# USAGE: ym_gen_header ()
function ( ym_gen_header )
  # ===================================================================
  # ヘッダファイルの検査
  # ===================================================================
  include (CheckIncludeFileCXX)
  check_include_file_cxx (stdlib.h    YM_HAVE_STDLIB_H)
  check_include_file_cxx (string.h    YM_HAVE_STRING_H)
  check_include_file_cxx (unistd.h    YM_HAVE_UNISTD_H)
  check_include_file_cxx (limits.h    YM_HAVE_LIMITS_H)
  check_include_file_cxx (float.h     YM_HAVE_FLOAT_H)
  check_include_file_cxx (math.h      YM_HAVE_MATH_H)
  check_include_file_cxx (sys/time.h  YM_HAVE_SYS_TIME_H)
  check_include_file_cxx (time.h      YM_HAVE_TIME_H)
  check_include_file_cxx (sys/stat.h  YM_HAVE_SYS_STAT_H)
  check_include_file_cxx (pwd.h       YM_HAVE_PWD_H)
  check_include_file_cxx (sys/param.h YM_HAVE_SYS_PARAM_H)

  if ( YM_HAVE_STDLIB_H )
    set ( INCLUDE_STDLIB "#include <stdlib.h>" )
  else ()
    set ( INCLUDE_STDLIB )
  endif ()

  if ( YM_HAVE_STRING_H )
    set ( INCLUDE_STRING "#include <string.h>" )
  else ()
    set ( INCLUDE_STRING )
  endif ()

  if ( YM_HAVE_UNISTD_H )
    set ( INCLUDE_UNISTD "#include <unistd.h>" )
  else ()
    set ( INCLUDE_UNISTD )
  endif ()

  if ( YM_HAVE_LIMITS_H )
    set ( INCLUDE_LIMITS "#include <limits.h>" )
  else ()
    set ( INCLUDE_LIMITS )
  endif ()

  if ( YM_HAVE_FLOAT_H )
    set ( INCLUDE_FLOAT "#include <float.h>" )
  else ()
    set ( INCLUDE_FLOAT )
  endif ()

  if ( YM_HAVE_MATH_H )
    set ( INCLUDE_MATH "#include <math.h>" )
  else ()
    set ( INCLUDE_MATH )
  endif ()


  # ===================================================================
  # ライブラリ関数の検査
  # ===================================================================
  include (CheckFunctionExists)
  check_function_exists (getrusage    YM_HAVE_GETRUSAGE)
  check_function_exists (times        YM_HAVE_TIMES)


  # ===================================================================
  # 組み込み型のサイズの検査
  # ===================================================================
  include (CheckTypeSize)
  check_type_size (int         INT_SIZE)
  check_type_size (long        LONG_SIZE)
  check_type_size ("long long" LLONG_SIZE)
  check_type_size ("void *"    VOIDP_SIZE)

  if ( INT_SIZE EQUAL VOIDP_SIZE )
    set( PTRINT_TYPE "unsigned int" )
  elseif ( LONG_SIZE EQUAL VOIDP_SIZE )
    set( PTRINT_TYPE "unsigned long" )
  elseif ( LLONG_SIZE EQUAL VOIDP_SIZE )
    set( PTRINT_TYPE "unsigned long long" )
  else ()
    # エラー
    message ( FATAL_ERROR
      "No valid type for pointer size integer" )
  endif ()

  # ヘッダファイルの生成
  configure_file(
    "${PROJECT_SOURCE_DIR}/ym-common/etc/ym_config.h.in"
    "${PROJECT_BINARY_DIR}/include/ym_config.h"
    )

endfunction()


# release, relwithdeb, debug ターゲットライブラリの設定
#
# USAGE: ym_add_object_library ( <target-name>
#                         <source-file> [<source-file>]
#                       )
function ( ym_add_object_library )
  foreach ( pos RANGE 0 ${ARGC} )
    if ( ${pos} EQUAL ${ARGC} )
      break()
    endif ()
    list (GET ARGV ${pos} argv)
    if ( ${pos} EQUAL 0 )
      # ターゲット名の設定
      # - 最適化モード
      # - プロファイルモード (_p)
      # - デバッグモード (_d)
      # の3つがある．
      set (_target_name   "${argv}_obj")
      set (_target_name_p "${argv}_obj_p")
      set (_target_name_d "${argv}_obj_d")
    else ()
      list (APPEND _sources ${argv})
    endif ()
  endforeach ()

  # release モードのターゲット
  add_library (${_target_name}
    OBJECT
    ${_sources}
    )

  target_compile_options (${_target_name}
    PRIVATE "-O3" "-fPIC"
    )

  target_compile_definitions (${_target_name}
    PRIVATE "-DNDEBUG"
    )

  # release with debug info モードのターゲット
  add_library (${_target_name_p}
    OBJECT
    ${_sources}
    )

  target_compile_options (${_target_name_p}
    PRIVATE "-O2" "-g" "-fPIC"
    )

  target_compile_definitions (${_target_name_p}
    PRIVATE "-DNDEBUG"
    )

  # debug モードのターゲット
  # 常に static にする．
  add_library (${_target_name_d}
    OBJECT
    ${_sources}
    )

  target_compile_options (${_target_name_d}
    PRIVATE "-g" "-fPIC"
    )

  target_compile_definitions (${_target_name_d}
    PRIVATE
    )

endfunction ()

# gtest 用のターゲットの生成
# USAGE: ym_add_gtest ( <target-name>
#                       <source-file> [<source-file>]
#                       ["DEFINITIONS" <definitions>]
#                     )
function( ym_add_gtest )
  set (_def_mode 0 )
  foreach ( _pos RANGE 0 ${ARGC} )
    if ( ${_pos} EQUAL ${ARGC} )
      break()
    endif ()
    list ( GET ARGV ${_pos} _arg )
    if ( ${_pos} EQUAL 0 )
      # ターゲット名の設定
      set ( _target_name   "${_arg}" )
    elseif ( ${_arg} STREQUAL "DEFINITIONS" )
      set ( _def_mode 1 )
    else ()
      if ( ${_def_mode} EQUAL 0 )
	list ( APPEND _sources ${_arg} )
      else ()
	set ( _definitions ${_arg} )
	set ( _def_mode 0 )
      endif ()
    endif ()
  endforeach ()

  add_executable ( ${_target_name}
    ${_sources}
    )

  target_compile_options ( ${_target_name}
    PRIVATE "-g" "-fPIC"
    )

  target_include_directories ( ${_target_name}
    PRIVATE ${GTEST_INCLUDE_DIRS}
    )

  if ( DEFINED _definitions )
    target_compile_definitions ( ${_target_name}
      PRIVATE ${_definitions}
      )
  endif ()

  target_link_libraries ( ${_target_name}
    ${YM_LIB_DEPENDS}
    pthread
    ${GTEST_BOTH_LIBRARIES}
    )

  add_test ( ${_target_name}
    ${_target_name}
    )

endfunction ()

# Doxygen 用のルール生成
#
# USAGE: ym_add_doxygen()
#
# 以下の準備が必要．
# - ${PROJECT_SOURCE_DIR}/etc/Doxyfile.in というテンプレートファイルを用意する．
# - CMAKE 変数 YM_DOXY_SRCS にスキャン対象のソースディレクトリをリストの
#   形で入れておく．
# - プロジェクト名とバージョンを連結した文字列を YM_PROJECT_STRING に入れておく．
macro ( ym_add_doxygen )
  # YM_DOXY_SRCS を Doxyfile の INPUT 用に変換する．
  string ( REPLACE ";" " " YM_DOXY_INPUT "${ARGV}" )

  # Doxyfile の生成
  configure_file (
    "${PROJECT_SOURCE_DIR}/etc/Doxyfile.in"
    "${PROJECT_BINARY_DIR}/Doxyfile"
    )

  # doxygen 用ターゲット
  add_custom_target(dox ALL
    DEPENDS "${PROJECT_BINARY_DIR}/docs/html/index.html"
    )

  cmake_policy( SET CMP0058 NEW )

  # doxygen 起動ルール
  add_custom_command(
    COMMAND "${DOXYGEN_EXECUTABLE}" ">" "doxygen.log"
    DEPENDS "${PROJECT_BINARY_DIR}/Doxyfile"
    DEPENDS ${ARGV}
    OUTPUT "${PROJECT_BINARY_DIR}/docs/html/index.html"
    COMMENT "generating doxygen documents"
    )

  # 生成物のインストールルール
  install (DIRECTORY
    "${PROJECT_BINARY_DIR}/docs"
    DESTINATION "share/${YM_PROJECT_STRING}"
    )

endmacro ( ym_add_doxygen )
