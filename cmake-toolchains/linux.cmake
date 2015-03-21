#-------------------------------------------------------------------------------
#   linux.cmake
#   Fips cmake settings file for Linux target platform.
#-------------------------------------------------------------------------------

message("Target Platform: Linux")
include(CheckFunctionExists)
include(CheckLibraryExists)

set(FIPS_PLATFORM Linux)
set(FIPS_PLATFORM_NAME "linux")
set(FIPS_LINUX 1)
set(FIPS_POSIX 1)

# define configuration types
set(CMAKE_CONFIGURATION_TYPES Debug Release)

if (FIPS_EXCEPTIONS)
    message("C++ exceptions are enabled")
    set(FIPS_LINUX_EXCEPTION_FLAGS "")
else()
    message("C++ exceptions are disabled")
    set(FIPS_LINUX_EXCEPTION_FLAGS "-fno-exceptions")
endif()

# C++ flags
set(CMAKE_CXX_FLAGS "${FIPS_LINUX_EXCEPTION_FLAGS} -std=c++11 -pthread -fno-strict-aliasing -Wno-multichar -Wall -Wextra -Wno-unused-parameter -Wno-unknown-pragmas -Wno-ignored-qualifiers")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -ftree-vectorize -msse3 -ffast-math -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-O0 -D_DEBUG_ -D_DEBUG -DFIPS_DEBUG=1 -ggdb")

# C flags
set(CMAKE_C_FLAGS "-pthread -fno-strict-aliasing -Wno-multichar -Wall -Wextra -Wno-unused-parameter -Wno-unknown-pragmas -Wno-ignored-qualifiers")        
set(CMAKE_C_FLAGS_RELEASE "-O3 -ftree-vectorize -msse3 -ffast-math -DNDEBUG")
set(CMAKE_C_FLAGS_DEBUG "-O0 -D_DEBUG_ -D_DEBUG -DFIPS_DEBUG=1 -ggdb")

# exe linker flags
set(CMAKE_EXE_LINKER_FLAGS "-pthread -dead_strip -lpthread -lrt")
set(CMAKE_EXE_LINKER_FLAGS_RELEASE "")
set(CMAKE_EXE_LINKER_FLAGS_DEBUG "")
if (FIPS_GCC)
    check_function_exists(__atomic_fetch_add_4 HAVE___ATOMIC_FETCH_ADD_4)
    if (NOT HAVE___ATOMIC_FETCH_ADD_4)
        check_library_exists(atomic __atomic_fetch_add_4 "" HAVE_LIBATOMIC)
        if (HAVE_LIBATOMIC)
            set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -latomic")
        endif()
    endif()
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

