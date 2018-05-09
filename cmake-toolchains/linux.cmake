#-------------------------------------------------------------------------------
#   linux.cmake
#   Fips cmake settings file for Linux target platform.
#-------------------------------------------------------------------------------

include(CheckFunctionExists)
include(CheckLibraryExists)

# Raspbian Linux flavour
option(FIPS_RASPBERRYPI "Set to true if compiling for the Raspberry Pi" OFF)

set(FIPS_PLATFORM Linux)
if (FIPS_RASPBERRYPI) 
    set(FIPS_PLATFORM_NAME "linuxraspbian")
else()
    set(FIPS_PLATFORM_NAME "linux")
endif()
set(FIPS_LINUX 1)
set(FIPS_POSIX 1)

# define configuration types
set(CMAKE_CONFIGURATION_TYPES Debug Release)

# C++ flags
set(CMAKE_CXX_FLAGS "-fPIC -std=c++11 -pthread -fno-strict-aliasing -Wno-expansion-to-defined -Wno-multichar -Wall -Wextra -Wno-unused-parameter -Wno-unknown-pragmas -Wno-ignored-qualifiers")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -ftree-vectorize -ffast-math -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-O0 -D_DEBUG_ -D_DEBUG -DFIPS_DEBUG=1 -ggdb")

# C flags
set(CMAKE_C_FLAGS "-fPIC -pthread -fno-strict-aliasing -Wno-multichar -Wall -Wextra -Wno-expansion-to-defined -Wno-unused-parameter -Wno-unknown-pragmas -Wno-ignored-qualifiers")
set(CMAKE_C_FLAGS_RELEASE "-O3 -ftree-vectorize -ffast-math -DNDEBUG")
set(CMAKE_C_FLAGS_DEBUG "-O0 -D_DEBUG_ -D_DEBUG -DFIPS_DEBUG=1 -ggdb")

# exe linker flags
set(CMAKE_EXE_LINKER_FLAGS "-pthread -dead_strip -lpthread")
set(CMAKE_EXE_LINKER_FLAGS_RELEASE "")
set(CMAKE_EXE_LINKER_FLAGS_DEBUG "")

# exceptions on/off?
if (NOT FIPS_EXCEPTIONS)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-exceptions")
endif()

# RTTI on/off?
if (NOT FIPS_RTTI)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-rtti")
endif()

# 32-bit build on/off?
if (FIPS_LINUX_MACH32)
    set(CMAKE_CXX_FLASG "${CMAKE_CXX_FLAGS} -m32")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -m32")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS -m32")
endif()

if (FIPS_GCC)
    check_function_exists(__atomic_fetch_add_4 HAVE___ATOMIC_FETCH_ADD_4)
    if (NOT HAVE___ATOMIC_FETCH_ADD_4)
        check_library_exists(atomic __atomic_fetch_add_4 "" HAVE_LIBATOMIC)
        if (HAVE_LIBATOMIC)
            set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -latomic")
        endif()
    endif()
endif()
check_library_exists(rt clock_gettime "time.h" FOUND_CLOCK_GETTIME)
if (FOUND_CLOCK_GETTIME)
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -lrt")
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

