#-------------------------------------------------------------------------------
#   windows-clang.cmake
#   fips cmake settings file for clang on Windows.
#-------------------------------------------------------------------------------

set(FIPS_PLATFORM WIN64)
set(FIPS_PLATFORM_NAME "win64")
set(FIPS_WIN64 1)
set(FIPS_WINDOWS 1)

set(CMAKE_CONFIGURATION_TYPES Debug Release)

set(CMAKE_C_COMPILER "clang" CACHE PATH "gcc" FORCE)
set(CMAKE_CXX_COMPILER "clang++" CACHE PATH "g++" FORCE)
set(CMAKE_AR "llvm-ar" CACHE PATH "archive" FORCE)

set(CMAKE_C_USE_RESPONSE_FILE_FOR_LIBRARIES 1)
set(CMAKE_CXX_USE_RESPONSE_FILE_FOR_LIBRARIES 1)
set(CMAKE_C_USE_RESPONSE_FILE_FOR_OBJECTS 1)
set(CMAKE_CXX_USE_RESPONSE_FILE_FOR_OBJECTS 1)
set(CMAKE_C_USE_RESPONSE_FILE_FOR_INCLUDES 1)
set(CMAKE_CXX_USE_RESPONSE_FILE_FOR_INCLUDES 1)
set(CMAKE_C_RESPONSE_FILE_LINK_FLAG "@")
set(CMAKE_CXX_RESPONSE_FILE_LINK_FLAG "@")

# C++ flags
set(CMAKE_CXX_FLAGS "-std=c++11 -fstrict-aliasing -Wno-deprecated-declarations -Wno-multichar -Wall -Wextra -Wno-unknown-pragmas -Wno-ignored-qualifiers -Wno-missing-field-initializers")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -D_DEBUG_ -D_DEBUG -DFIPS_DEBUG=1")

# C flags
set(CMAKE_C_FLAGS "-fstrict-aliasing -Wno-deprecated-declarations -Wno-multichar -Wall -Wextra -Wno-unknown-pragmas -Wno-ignored-qualifiers -Wno-missing-field-initializers")
set(CMAKE_C_FLAGS_RELEASE "-O3 -DNDEBUG")
set(CMAKE_C_FLAGS_DEBUG "-g -O0 -D_DEBUG_ -D_DEBUG -DFIPS_DEBUG=1")

# exe linker flags
set(CMAKE_EXE_LINKER_FLAGS "")
set(CMAKE_EXE_LINKER_FLAGS_RELEASE "-llibcmt")
set(CMAKE_EXE_LINKER_FLAGS_DEBUG "-g -llibcmtd")

# DLL linker flags
set(CMAKE_SHARED_LINKER_FLAGS "")
set(CMAKE_SHARED_LINKER_FLAGS_RELEASE "-llibcmt")
set(CMAKE_SHARED_LINKER_FLAGS_DEBUG "-g -llibcmtd")

# exceptions on/off?
if (NOT FIPS_EXCEPTIONS)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-exceptions")
endif()

# RTTI on/off?
if (NOT FIPS_RTTI)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")
endif()

# clang address sanitizer?
if (FIPS_CLANG_ADDRESS_SANITIZER)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=address")
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