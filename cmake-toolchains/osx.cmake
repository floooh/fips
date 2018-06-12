#-------------------------------------------------------------------------------
#	osx.cmake
#	Fips cmake settings file for OSX target platform.
#-------------------------------------------------------------------------------

set(FIPS_PLATFORM OSX)
set(FIPS_PLATFORM_NAME "osx")
set(FIPS_MACOS 1)
set(FIPS_OSX 1)
set(FIPS_POSIX 1)

# define configuration types
set(CMAKE_CONFIGURATION_TYPES Debug Release)

if (FIPS_OSX_UNIVERSAL)
    set(CMAKE_OSX_ARCHITECTURES "i386;x86_64")
endif()

# FIXME: define standard frame works that are always linked
set(FIPS_OSX_STANDARD_FRAMEWORKS Foundation IOKit)

# globally silence the GL depreciation warning
add_definitions(-DGL_SILENCE_DEPRECATION)

# compiler flags
set(CMAKE_CXX_FLAGS "-std=c++11 -fstrict-aliasing -Wno-expansion-to-defined -Wno-multichar -Wall -Wextra -Wno-unused-parameter -Wno-unknown-pragmas -Wno-ignored-qualifiers -Wno-long-long -Wno-overloaded-virtual -Wno-unused-volatile-lvalue -Wno-deprecated-writable-strings")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -msse3 -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-O0 -D_DEBUG_ -D_DEBUG -DFIPS_DEBUG=1 -ggdb")

set(CMAKE_C_FLAGS "-fstrict-aliasing -Wno-multichar -Wall -Wextra -Wno-expansion-to-defined -Wno-unused-parameter -Wno-unknown-pragmas -Wno-ignored-qualifiers -Wno-long-long -Wno-overloaded-virtual -Wno-unused-volatile-lvalue  -Wno-deprecated-writable-strings")
set(CMAKE_C_FLAGS_RELEASE "-O3 -msse3 -DNDEBUG")
set(CMAKE_C_FLAGS_DEBUG "-O0 -D_DEBUG_ -D_DEBUG -DFIPS_DEBUG=1 -g")        	

set(CMAKE_EXE_LINKER_FLAGS "-ObjC -dead_strip -lpthread")
set(CMAKE_EXE_LINKER_FLAGS_DEBUG "")
set(CMAKE_EXE_LINKER_FLAGS_RELEASE "")

# need to set some flags directly as Xcode attributes
set(CMAKE_XCODE_ATTRIBUTE_CLANG_CXX_LANGUAGE_STANDARD "c++11")
set(CMAKE_XCODE_ATTRIBUTE_CLANG_CXX_LIBRARY "libc++")

# ARC on/off?
option(FIPS_OSX_USE_ARC "Enable/disable Automatic Reference Counting" OFF)
if (FIPS_OSX_USE_ARC)
    set(CMAKE_XCODE_ATTRIBUTE_CLANG_ENABLE_OBJC_ARC "YES")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fobjc-arc")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fobjc-arc")
else()
    set(CMAKE_XCODE_ATTRIBUTE_CLANG_ENABLE_OBJC_ARC "NO")
endif()

# exceptions on/off?
if (FIPS_EXCEPTIONS)
    set(CMAKE_XCODE_ATTRIBUTE_GCC_ENABLE_CPP_EXCEPTIONS "YES")
else()
    set(CMAKE_XCODE_ATTRIBUTE_GCC_ENABLE_CPP_EXCEPTIONS "NO")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-exceptions")
endif()

# rtti on/off?
if (FIPS_RTTI)
    set(CMAKE_XCODE_ATTRIBUTE_GCC_ENABLE_CPP_RTTI "YES")
else()
    set(CMAKE_XCODE_ATTRIBUTE_GCC_ENABLE_CPP_RTTI "NO")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")
endif()

# clang address sanitizer?
if (FIPS_CLANG_ADDRESS_SANITIZER)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=address")
endif()

# clang 'save-optimization-record'?
if (FIPS_CLANG_SAVE_OPTIMIZATION_RECORD)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsave-optimization-record")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsave-optimization-record")
endif()

# update cache variables for cmake gui
set(CMAKE_CONFIGURATION_TYPES "${CMAKE_CONFIGURATION_TYPES}" CACHE STRING "Config Type" FORCE)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}" CACHE STRING "Generic C++ Compiler Flags" FORCE)
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}" CACHE STRING "C++ Debug Compiler Flags" FORCE)
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}" CACHE STRING "C++ Release Compiler Flags" FORCE)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}" CACHE STRING "Generic C Compiler Flags" FORCE)
set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG}" CACHE STRING "C Debug Compiler Flags" FORCE)
set(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE}" CACHE STRING "C Release Compiler Flags" FORCE)
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS}" CACHE STRING "Generic Linker Flags" FORCE)
set(CMAKE_EXE_LINKER_FLAGS_DEBUG "${CMAKE_EXE_LINKER_FLAGS_DEBUG}" CACHE STRING "Debug Linker Flags" FORCE)
set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE}" CACHE STRING "Release Linker Flags" FORCE)

# set the build type to use
if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Debug" CACHE STRING "Compile Type" FORCE)
endif()
set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS Debug Release)

