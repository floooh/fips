#-------------------------------------------------------------------------------
#   fips.cmake
#   Main cmake header for fips, this must be included in the top-level
#   CMakeLists.txt file of a fips project
#-------------------------------------------------------------------------------
if (${CMAKE_VERSION} VERSION_GREATER 3.0)
    cmake_policy(SET CMP0042 NEW)
endif()

get_filename_component(FIPS_PROJECT_DIR "." ABSOLUTE)
get_filename_component(FIPS_PROJECT_NAME ${FIPS_PROJECT_DIR} NAME)
if (FIPS_LOCAL_BUILD)
    get_filename_component(FIPS_DEPLOY_DIR "${FIPS_PROJECT_DIR}/fips-files/deploy" ABSOLUTE)
    get_filename_component(FIPS_BUILD_DIR "${FIPS_PROJECT_DIR}/fips-files/build" ABSOLUTE)
else()
    get_filename_component(FIPS_DEPLOY_DIR "${FIPS_ROOT_DIR}/../fips-deploy" ABSOLUTE)
    get_filename_component(FIPS_BUILD_DIR "${FIPS_ROOT_DIR}/../fips-build" ABSOLUTE)
endif()

include(CMakeParseArguments)

include("${FIPS_ROOT_DIR}/cmake/fips_private.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_platform.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_generators.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_deprecated.cmake")

#-------------------------------------------------------------------------------
#   define top-level options for the whole project
#-------------------------------------------------------------------------------
option(FIPS_CMAKE_VERBOSE "Verbose messages during cmake runs" OFF)
option(FIPS_EXCEPTIONS "Enable C++ exceptions" OFF)
option(FIPS_RTTI "Enable C++ RTTI" OFF)
option(FIPS_COMPILE_VERBOSE "Enable very verbose compilation" OFF)
option(FIPS_PROFILING "Enable app profiling/tracing" OFF)
option(FIPS_OSX_UNIVERSAL "Enable generation of universal binaries on OS X" OFF)
option(FIPS_LINUX_MACH32 "Enable 32-bit code generation on 64-bit Linux host" OFF)
option(FIPS_AUTO_IMPORT "Automatically include all modules from imports" ON)
option(FIPS_CLANG_ADDRESS_SANITIZER "Enable clang address sanitizer" OFF)
option(FIPS_CLANG_SAVE_OPTIMIZATION_RECORD "Enable clang -fsave-optimization-record option" OFF)
option(FIPS_DYNAMIC_CRT "Use dynamically linked CRT on Windows" ON)

#-------------------------------------------------------------------------------
#   fips_setup()
#   Performs one-time initialization of the build system. Must be called
#   at the start of the root CMakeLists.txt file.
#
macro(fips_setup)

    #
    # cmake 3.15 has added a warning if the top-level cmake file doesn't contain
    # a project() statement, so we'll expect that the project name is now
    # set directly before fips_setup() is called, and only support the
    # PROJECT args for backward compatibility
    #
    if (CMAKE_PROJECT_NAME STREQUAL "Project")
        message(WARNING "please call project([proj_name]) directly before fips_setup(), cmake is expecting this starting with version 3.15")
        #
        # check for optional main-project name, this is the preferred way to
        # define the project name, but we better be backward compatible
        # it is still allowed to call fips_project() afterwards
        #
        # if a project imports Apps or SharedLibs, fips_setup MUST contain a PROJECT arg
        set(options)
        set(oneValueArgs PROJECT)
        set(multiValueArgs)
        CMAKE_PARSE_ARGUMENTS(_fs "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
        if (_fs_UNPARSED_ARGUMENTS)
            message(FATAL_ERROR "fips_setup(): called with invalid args '${_fg_UNPARSED_ARGUMENTS}'")
        endif()
        if (_fs_PROJECT)
            project(${_fs_PROJECT})
            message("=== fips_setup(PROJECT ${_fs_PROJECT})")
        else()
            message("=== fips_setup()")
        endif()
    endif()
    message("CMAKE_BUILD_TYPE: ${CMAKE_BUILD_TYPE}")

    if (FIPS_ROOT_DIR)
        message("FIPS_ROOT_DIR: ${FIPS_ROOT_DIR}")
    else()
        message(FATAL_ERROR "Must specify absolute FIPS_ROOT_DIR before calling fips_setup()!")
    endif()
    if (FIPS_PROJECT_DIR)
        message("FIPS_PROJECT_DIR: ${FIPS_PROJECT_DIR}")
    else()
        message(FATAL_ERROR "Must specify absolute FIPS_PROJECT_DIR before calling fips_setup()!")
    endif()
    message("FIPS_BUILD_DIR: ${FIPS_BUILD_DIR}")
    if (FIPS_DEPLOY_DIR)
        message("FIPS_DEPLOY_DIR: ${FIPS_DEPLOY_DIR}")
    else()
        message(FATAL_ERROR "Must specify absolute FIPS_DEPLOY_DIR before calling fips_setup()!")
    endif()
    message("FIPS_PROJECT_NAME: ${FIPS_PROJECT_NAME}")
    message("FIPS_AUTO_IMPORT: ${FIPS_AUTO_IMPORT}")

    # set FIPS_CONFIG to default if not provided by command line
    # (this provides better compatibility with some IDEs not directly
    # supported by cmake, like QtCreator
    if (NOT FIPS_CONFIG)
        message("FIPS_CONFIG not provided by command line, selecting default value")
        fips_choose_config()
    endif()
    message("FIPS_CONFIG: ${FIPS_CONFIG}")
    get_filename_component(FIPS_PROJECT_BUILD_DIR "${FIPS_BUILD_DIR}/${FIPS_PROJECT_NAME}/${FIPS_CONFIG}" ABSOLUTE)
    message("FIPS_PROJECT_BUILD_DIR: ${FIPS_PROJECT_BUILD_DIR}")
    get_filename_component(FIPS_PROJECT_DEPLOY_DIR "${FIPS_DEPLOY_DIR}/${FIPS_PROJECT_NAME}/${FIPS_CONFIG}" ABSOLUTE)
    message("FIPS_PROJECT_DEPLOY_DIR: ${FIPS_PROJECT_DEPLOY_DIR}")

    # set host system variables
    set (FIPS_HOST_WINDOWS 0)
    set (FIPS_HOST_OSX 0)
    set (FIPS_HOST_LINUX 0)
    if (${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Windows")
        set(FIPS_HOST_WINDOWS 1)
        message("Host system: Windows")
    elseif (${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Darwin")
        set(FIPS_HOST_OSX 1)
        message("Host system: OSX")
    elseif (${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Linux")
        set(FIPS_HOST_LINUX 1)
        message("Host system: Linux")
    else()
        message(WARNING "Host system not recognized, setting to 'Linux'")
        set(FIPS_HOST_LINUX 1)
    endif()

    # detect compiler
    message("CMAKE_CXX_COMPILER_ID: ${CMAKE_CXX_COMPILER_ID}")
    if (${CMAKE_CXX_COMPILER_ID} MATCHES "Clang")
        set(FIPS_CLANG 1)
        message("FIPS_CLANG: 1")
        if (${CMAKE_CXX_COMPILER_ID} MATCHES "AppleClang")
            set(FIPS_APPLE_CLANG 1)
            message("FIPS_APPLE_CLANG: 1")
        endif()
    elseif (${CMAKE_CXX_COMPILER_ID} MATCHES "GNU")
        set(FIPS_GCC 1)
        message("FIPS_GCC: 1")
    elseif (MSVC)
        set(FIPS_MSVC 1)
        message("FIPS_MSVC: 1")
    else()
        if (FIPS_EMSCRIPTEN)
            set(FIPS_CLANG 1)
            message("FIPS_CLANG: 1")
        elseif (FIPS_ANDROID)
            set(FIPS_CLANG 1)
            message("FIPS_CLANG: 1")
        else()
            message("Detected C++ Compiler: Unknown")
        endif()
    endif()

    # Eclipse: Disable linked resources because Eclipse may get confused by these linked resources
    if (${CMAKE_GENERATOR} MATCHES "Eclipse CDT4")
        set(CMAKE_ECLIPSE_GENERATE_LINKED_RESOURCES OFF)
        set(CMAKE_ECLIPSE_GENERATE_SOURCE_PROJECT ON)
        set(CMAKE_ECLIPSE_VERSION "4.3" CACHE STRING "Eclipse version")
    endif()

    # manually include "toolchain" files for non-crosscompiling scenarios
    if (NOT CMAKE_TOOLCHAIN_FILE)
        if (FIPS_HOST_WINDOWS)
            include(${FIPS_ROOT_DIR}/cmake-toolchains/windows.cmake)
        elseif (FIPS_HOST_OSX)
            include(${FIPS_ROOT_DIR}/cmake-toolchains/osx.cmake)
        else()
            include(${FIPS_ROOT_DIR}/cmake-toolchains/linux.cmake)
        endif()
    endif()
    message("FIPS_PLATFORM: " ${FIPS_PLATFORM})
    message("FIPS_PLATFORM_NAME: ${FIPS_PLATFORM_NAME}")

    # setup standard link directories
    fips_setup_link_directories()

    # setup the target group variable, used to group targets into folders in IDEs
    set_property(GLOBAL PROPERTY USE_FOLDERS ON)

    # check whether python is installed
    # find_package finds Windows Store installed Python. find_program does not.
    find_package(Python)
    if (NOT Python_FOUND)
        message(FATAL_ERROR "Python not found, required for code generation!")
    endif()

    set(PYTHON ${Python_EXECUTABLE})

    # write empty YAML property tracking files
    fips_init_targets_list()

    # initialize code generation
    fips_init_codegen()

    # load project-local fips-include.cmake if exists
    if (EXISTS "${FIPS_PROJECT_DIR}/fips-include.cmake")
        include("${FIPS_PROJECT_DIR}/fips-include.cmake")
    elseif (EXISTS "${FIPS_PROJECT_DIR}/fips-files/include.cmake")
        include("${FIPS_PROJECT_DIR}/fips-files/include.cmake")
    endif()

    # load generated .fips-imports.cmake if exists
    if (EXISTS "${FIPS_PROJECT_DIR}/.fips-imports.cmake")
        include("${FIPS_PROJECT_DIR}/.fips-imports.cmake")
    endif()

endmacro()

#-------------------------------------------------------------------------------
#   fips_ide_group(group)
#   Define the IDE group name for the following targets.
#
macro(fips_ide_group group)
    set(FIPS_TARGET_GROUP ${group})
endmacro()

#-------------------------------------------------------------------------------
#   fips_begin_lib(name)
#
#   Begin defining a static link library. fips_end_module() is a backward
#   compatibility alias for fips_begin_lib()
#
macro(fips_begin_lib target)
    if (FIPS_CMAKE_VERBOSE)
        message("lib: name=" ${target})
    endif()
    fips_reset(${target})
    add_library(${target})
    fips_apply_target_ide_group(${target})
    fips_msvc_add_target_properties(${target})
    fips_add_to_targets_list(${target} "lib")
endmacro()

#-------------------------------------------------------------------------------
#   fips_end_lib(name)
#   End defining a static link library.
#
macro(fips_end_lib)
    fips_handle_generators(${CurTargetName})
endmacro()

#-------------------------------------------------------------------------------
#   fips_begin_app(target type)
#   Start defining a new app.
#   Type can be "windowed" or "cmdline", default is "cmdline".
#
macro(fips_begin_app target type)
    if (FIPS_CMAKE_VERBOSE)
        message("app: name=" ${target} " type=" ${type})
    endif()
    if (${type} STREQUAL "windowed" OR ${type} STREQUAL "cmdline")
        fips_reset(${target})
        if (${type} STREQUAL "windowed")
            if (FIPS_OSX)
                add_executable(${target} MACOSX_BUNDLE)
            elseif (FIPS_WIN32 OR FIPS_WIN64)
                add_executable(${target} WIN32)
            elseif (FIPS_ANDROID)
                add_library(${target} SHARED)
            else()
                add_executable(${target})
            endif()
            target_compile_definitions(${target} PRIVATE FIPS_APP_WINDOWED=1)
        else()
            if (FIPS_ANDROID)
                add_library(${target} SHARED)
            else()
                add_executable(${target})
            endif()
            target_compile_definitions(${target} PRIVATE FIPS_APP_CMDLINE=1)
        endif()
        fips_apply_target_ide_group(${target})
        fips_config_output_directory(${target})
        fips_config_postfixes_for_exe(${target})
        fips_msvc_add_target_properties(${target})
        fips_windows_copy_target_dlls(${target})
        fips_android_postbuildstep(${target})
        fips_add_to_targets_list(${target} "app")
    else()
        message(FATAL_ERROR "type must be \"windowed\" or \"cmdline\"!")
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_end_app()
#   End defining an application.
#
macro(fips_end_app)
    fips_handle_generators(${CurTargetName})
    fips_osx_add_target_properties(${CurTargetName})
endmacro()

#-------------------------------------------------------------------------------
#   fips_begin_sharedlib(name)
#   Begin a fips shared library.
#
macro(fips_begin_sharedlib target)
    if (FIPS_CMAKE_VERBOSE)
        message("shared lib: name=" ${target})
    endif()
    fips_reset(${target})
    add_library(${target} SHARED)
    fips_apply_target_ide_group(${target})
    fips_msvc_add_target_properties(${target})
    fips_config_output_directory(${target})
    fips_add_to_targets_list(${target} "sharedlib")
endmacro()

#-------------------------------------------------------------------------------
#   fips_end_sharedlib()
#   End defining a shared library.
#
macro(fips_end_sharedlib)
    fips_handle_generators(${CurTargetName})
endmacro()

#-------------------------------------------------------------------------------
#   fips_libs(libs ...)
#   fips_deps(libs ...)
#
#   Add one or more static link library dependencies to the current target.
#   (note that fips_deps() is simply an alias of fips_libs).
#
macro(fips_libs libs)
    foreach(lib ${ARGV})
        target_link_libraries(${CurTargetName} ${lib})
    endforeach()
endmacro()
macro(fips_deps libs)
    set(_libs ${libs} ${ARGN})
    fips_libs("${_libs}")
endmacro()

#-------------------------------------------------------------------------------
#   fips_libs_debug(libs ...)
#   Add one or more static link library that are only used in debug mode.
#   This is sometimes necessary for precompiled visual studio libs (if they
#   use STL code).
#   NOTE: libraries with fips_libs_debug() have no recursive dependency
#   resolution.
#
macro(fips_libs_debug libs)
    foreach(lib ${ARGV})
        target_link_libraries(${target} debug ${lib})
    endforeach()
endmacro()

#-------------------------------------------------------------------------------
#   fips_libs_release(libs ...)
#   Same as fips_libs_debug(), but for release mode (or rather: all non-debug
#   modes).
#
macro(fips_libs_release libs)
    foreach(lib ${ARGV})
        target_link_libraries(${target} optimized ${lib})
    endforeach()
endmacro()

#-------------------------------------------------------------------------------
#   fips_dir(dir [GROUP ide_group])
#   Enter a source code subdirectory.
#
macro(fips_dir dir)
    # parse args
    set(options)
    set(oneValueArgs GROUP)
    set(multiValueArgs)
    CMAKE_PARSE_ARGUMENTS(_fd "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
    if (_fg_UNPARSED_ARGUMENTS)
        message(FATAL_ERROR "fips_dir(): called with invalid args '${_fg_UNPARSED_ARGUMENTS}'")
    endif()

    # assign CurDir global var
    if (${dir} STREQUAL ".")
        set(CurDir)
    else()
        set(CurDir "${dir}/")
    endif()

    # assign CurGroup global var
    if (_fd_GROUP)
        # group is explicitly given as GROUP argument
        set(CurGroup ${_fd_GROUP})
        # special case 'no group' as GROUP "."
        if (${CurGroup} STREQUAL ".")
            set(CurGroup "")
        endif()
    elseif (${dir} STREQUAL ".")
        set(CurGroup "")
    else()
        # otherwise derive from directory path
        # hack to string the leading '/' from CurDir
        set(CurGroup "${CurDir}")
        string(REPLACE "/!" "" CurGroup "${CurGroup}")
    endif()
    string(REPLACE / \\\\ CurGroup "${CurGroup}")
endmacro()

#-------------------------------------------------------------------------------
#   fips_files(files ...)
#   Add files to current target.
#
macro(fips_files files)
    foreach (cur_file ${ARGV})
        fips_add_file(${cur_file} ".py" "NO_GENERATOR" "NO_GENFILES")
    endforeach()
endmacro()

#-------------------------------------------------------------------------------
#   fips_files_ex(path [globbing expressions ...]
#       [EXCEPT globbing expressions ...]
#       [GROUP ide_group]
#       [NO_RECURSE]
#       [GROUP_FOLDERS])
#
#   Add files from a path to the current target by using globbing expression.
#   It also creates and IDE group.
#
#   EXCEPT:   globbing expressions on files to exclude
#   GROUP:    the same as fips_dir GROUP, used for grouping files in a project
#   NO_RECURSE: do not use GLOB_RECURSE on globbing expressions
#   GROUP_FOLDERS: will create groups based on folders
#
#   Note: fips_dir is used internally, so the current dir will change and you
#   will be able to more operation on this dir as fips_files().
#
macro(fips_files_ex path)
    set(options NO_RECURSE GROUP_FOLDERS)
    set(oneValueArgs GROUP)
    set(multiValueArgs EXCEPT)
    CMAKE_PARSE_ARGUMENTS(_fd "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
    if (_fg_UNPARSED_ARGUMENTS)
        message(FATAL_ERROR "fips_files_ex(): called with invalid args '${_fg_UNPARSED_ARGUMENTS}'")
    endif()

    if (NOT _bs_GROUP)
        set(_bs_GROUP ".")
    endif()

    set(path "./${path}/")
    file(TO_CMAKE_PATH ${path} path)

    set(ARG_LIST ${ARGV})
    list(REMOVE_AT ARG_LIST 0)

    set(_fd_FILE_LIST "")
    foreach (_fd_glob_expr ${ARG_LIST})
        if (_fd_NO_RECURSE)
            file(GLOB _fd_TMP RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/${path} "${path}/${_fd_glob_expr}")
        else()
            file(GLOB_RECURSE _fd_TMP RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/${path} "${path}/${_fd_glob_expr}")
        endif()
        list(APPEND _fd_FILE_LIST ${_fd_TMP})
    endforeach()

    if (_fd_EXCEPT)
        set(_fd_EXCEPT_FILE_LIST "")
        foreach (_fd_glob_expr ${_fd_EXCEPT})
            if (_fd_NO_RECURSE)
                file(GLOB _fd_TMP RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/${path} "${path}/${_fd_glob_expr}")
            else()
                file(GLOB_RECURSE _fd_TMP RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/${path} "${path}/${_fd_glob_expr}")
            endif()
            list(APPEND _fd_EXCEPT_FILE_LIST ${_fd_TMP})
        endforeach()
        list(LENGTH _fd_EXCEPT_FILE_LIST _has_files)
        if (_has_files)
            list(REMOVE_ITEM _fd_FILE_LIST ${_fd_EXCEPT_FILE_LIST})
        endif()
    endif()

    if (_fd_FILE_LIST)
        if (_fd_GROUP_FOLDERS)
            fips_dir_groups("${path}" "${_fd_FILE_LIST}")
        else()
            fips_dir(${path} GROUP ${_fd_GROUP})
            fips_files(${_fd_FILE_LIST})
        endif()
    else()
        message(WARNING "Empty file list for path '${path}' (maybe path doesn't exist?)")
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_src(path [globbing expressions ...]
#       [EXCEPT globbing expressions ...]
#       [GROUP ide_group]
#       [NO_RECURSE])
#
#   Enter a source code subdirectory and collect C/C++ source and header files
#   (*.c, *.cc, *.cpp, *.h, *.hh, *.hpp)
#   Note that Objective-C aren't automatically considered, for these files use
#   fips_files() or fips_files_ex().
#
#   EXCEPT:   globbing expressions on files to exclude
#   GROUP:    the same as fips_dir GROUP, used for grouping files in a project
#   NO_RECURSE: do not use GLOB_RECURSE on globbing expressions
#
#   Note: fips_dir is used internally, so the current dir will change and you
#   will be able to more operation on this dir as fips_files().
#
macro(fips_src path)
    fips_files_ex(${path} *.c *.cc *.cpp *.h *.hh *.hpp ${ARGV})
endmacro()

#-------------------------------------------------------------------------------
#   fips_generate(FROM input_file
#       [TYPE generator_type]
#       [SOURCE output_source]
#       [HEADER output_header]
#       [ARGS args_in_yaml_format]
#       [REQUIRES target]
#       [OUT_OF_SOURCE])
#
#   Generate one C/C++ source/header pair from an input definition file
#   by running a python generator script.
#
#   FROM:     name of an input file to be processed
#   TYPE:     the generator type, filename of a generator script with the .py
#   SOURCE:   name of generated source file
#   HEADER:   name of generated header file
#   ARGS:     optional key/value arguments handed to generator script as dict
#   REQUIRES: optional target required to exist or be built before generation
#   OUT_OF_SOURCE:  if present, put the generated sources into the build
#                   directory, not the source code directory
#
#   If no TYPE is provided, the input_file must be a python script.
#
#   If both SOURCE and HEADER are omitted, it is assumed that the
#   generator script generated a input_file.cc/input_file.h pair.
#   Omitting one of SOURCE or HEADER means the generator script
#   will only generate either the SOURCE or HEADER file.
#
#   NOTE: when using REQUIRES the target must exist to be considered, otherwise
#   it will ignore the directive. The order on which the targets are defined
#   is important, so define required targets BEFORE requiring generators.
#
macro(fips_generate)
    set(options OUT_OF_SOURCE)
    set(oneValueArgs FROM TYPE SOURCE HEADER ARGS REQUIRES SRC_EXT HDR_EXT)
    set(multiValueArgs)
    CMAKE_PARSE_ARGUMENTS(_fg "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
    if (_fg_UNPARSED_ARGUMENTS)
        message(FATAL_ERROR "fips_generate(): called with invalid args '${_fg_UNPARSED_ARGUMENTS}'")
    endif()
    if (NOT _fg_FROM)
        message(FATAL_ERROR "fips_generate(): FROM arg required")
    endif()
    if (NOT _fg_SRC_EXT)
        set(_fg_SRC_EXT ".cc")
    endif()
    if (NOT _fg_HDR_EXT)
        set(_fg_HDR_EXT ".h")
    endif()
    if (NOT _fg_SOURCE AND NOT _fg_HEADER)
        # if both no SOURCE and no HEADER provided, set both
        # to input file plus .cc / .h extension
        get_filename_component(f_ext ${_fg_FROM} EXT)
        string(REPLACE ${f_ext} ${_fg_SRC_EXT} _fg_SOURCE ${_fg_FROM})
        string(REPLACE ${f_ext} ${_fg_HDR_EXT} _fg_HEADER ${_fg_FROM})
    endif()
    if (_fg_REQUIRES)
        fips_add_target_dependency(${_fg_REQUIRES})
    endif()
    fips_add_file("${_fg_FROM}")
    fips_add_generator(${CurTargetName} "${_fg_TYPE}" ${_fg_OUT_OF_SOURCE} "${_fg_FROM}" "${_fg_SOURCE}" "${_fg_HEADER}" "${_fg_ARGS}")
endmacro()
