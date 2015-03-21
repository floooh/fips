#-------------------------------------------------------------------------------
#	windows.cmake
#	fips cmake settings file for Windows platform (supports 32- and 64-bit)
#-------------------------------------------------------------------------------

# detect 32-bit or 64-bit target platform   
if (CMAKE_CL_64)
	message("Target Platform: Windows 64-bit")
    set(FIPS_PLATFORM WIN64)
    set(FIPS_PLATFORM_NAME "win64")
    set(FIPS_WIN64 1)
    set(FIPS_WINDOWS 1)
    set(FIPS_WINDOWS_PLATFORM_NAME "x64")
else()
	message("Target Platform: Windows 32-bit")
    set(FIPS_PLATFORM WIN32)
    set(FIPS_PLATFORM_NAME "win32")
    set(FIPS_WIN32 1)
    set(FIPS_WINDOWS 1)
    set(FIPS_WINDOWS_PLATFORM_NAME "x86")
endif()

# define configuration types
set(CMAKE_CONFIGURATION_TYPES Debug Release)

# define the standard link libraries
set(CMAKE_CXX_STANDARD_LIBRARIES "kernel32.lib user32.lib gdi32.lib winspool.lib shell32.lib ole32.lib oleaut32.lib uuid.lib comdlg32.lib advapi32.lib dbghelp.lib wsock32.lib ws2_32.lib rpcrt4.lib wininet.lib")
set(CMAKE_C_STANDARD_LIBRARIES "kernel32.lib user32.lib gdi32.lib winspool.lib shell32.lib ole32.lib oleaut32.lib uuid.lib comdlg32.lib advapi32.lib dbghelp.lib wsock32.lib ws2_32.lib rpcrt4.lib wininet.lib")

# define compiler and linker flags

# GENERIC compiler flags:
# 	/WX treat warnings as errors
# 	/GF eliminate duplicate strings
# 	/arch:SSE2 generate code for SSE2
# 	/TP treat files as C++ source
#	/TC treat files as C source
# 	/fp:fast create fast (not precise) floating point code
# 	/Gm: enable minimal rebuild
#	/EHsc: slim exception model
#	/EHa: fat exception model
#   /MP: use multiple cores
#
# DEBUG compiler flags:
#	/Zi create debugging information PDB file
#	/Od disable optimizations
# 	/Oy- do not suppress frame pointers (recommended for debugging)
#	/MTd use statically linked, thread-safe, debug CRT libs
#
# RELEASE compiler flags:
#	/Ox full optimization
#	/MT use statically linked, thread-safe CRT libs
# 	/GS- no Buffer Security Check
#	
if (FIPS_EXCEPTIONS)
    message("C++ exceptions are enabled")
    set(FIPS_VS_EXCEPTION_FLAGS "/EHa")
else()
    message("C++ exceptions are disabled")
    set(FIPS_VS_EXCEPTION_FLAGS "/EHsc")
endif()
set(CMAKE_CXX_FLAGS "${FIPS_VS_EXCEPTION_FLAGS} /MP /WX /TP /DWIN32")
set(CMAKE_CXX_FLAGS_DEBUG "/Zi /Od /Oy- /MTd /D_DEBUG /DFIPS_DEBUG=1")
set(CMAKE_CXX_FLAGS_RELEASE "/Ox /MT /DNDEBUG")

set(CMAKE_C_FLAGS "/MP /WX /TC /errorReport:queue /DWIN32")
set(CMAKE_C_FLAGS_DEBUG "/Zi /Od /Oy- /MTd /D_DEBUG /DFIPS_DEBUG=1")
set(CMAKE_C_FLAGS_RELEASE "/Ox /MT /DNDEBUG ")

# define exe linker flags
set(CMAKE_EXE_LINKER_FLAGS "/STACK:5000000 /machine:${FIPS_WINDOWS_PLATFORM_NAME}")
set(CMAKE_EXE_LINKER_FLAGS_DEBUG "/DEBUG")
set(CMAKE_EXE_LINKER_FLAGS_RELEASE "")

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

