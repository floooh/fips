#-------------------------------------------------------------------------------
#   fips.cmake
#   Main cmake header for fips, this must be included in the top-level
#   CMakeLists.txt file of a fips project
#-------------------------------------------------------------------------------
if (${CMAKE_VERSION} VERSION_GREATER 3.0)
    cmake_policy(SET CMP0042 NEW)
endif()

get_filename_component(FIPS_PROJECT_DIR "." ABSOLUTE)
get_filename_component(FIPS_DEPLOY_DIR "../fips-deploy" ABSOLUTE)

include(CMakeParseArguments)

include("${FIPS_ROOT_DIR}/cmake/fips_private.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_unittests.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_windows.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_android.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_osx.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_pnacl.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_generators.cmake")

#-------------------------------------------------------------------------------
#   define top-level options for the whole project
#-------------------------------------------------------------------------------
option(FIPS_CMAKE_VERBOSE "Verbose messages during cmake runs" OFF)
option(FIPS_NO_ASSERTS_IN_RELEASE "Remove asserts in release-mode" OFF)
option(FIPS_UNITTESTS "Enable unit tests" OFF)
option(FIPS_UNITTESTS_RUN_AFTER_BUILD "Automatically run unit tests after building" OFF)
option(FIPS_UNITTESTS_HEADLESS "If enabled don't run tests which require a display" OFF)
option(FIPS_EXCEPTIONS "Enable C++ exceptions" OFF)
option(FIPS_RTTI "Enable C++ RTTI" OFF)
option(FIPS_ALLOCATOR_DEBUG "Enable allocator debugging code (slow)" OFF)
option(FIPS_COMPILE_VERBOSE "Enable very verbose compilation" OFF)
option(FIPS_USE_CCACHE "Enable ccache when building with gcc or clang" OFF)
option(FIPS_PROFILING "Enable app profiling/tracing" OFF)
option(FIPS_OSX_UNIVERSAL "Enable generation of universal binaries on OS X" OFF)
option(FIPS_LINUX_MACH32 "Enable 32-bit code generation on 64-bit Linux host" OFF)
option(FIPS_AUTO_IMPORT "Automatically include all modules from imports" ON)

# turn some dependent options on/off
if (FIPS_UNITTESTS)
    enable_testing()
    set(FIPS_EXCEPTIONS ON CACHE BOOL "Enable C++ exceptions" FORCE)
endif()

#-------------------------------------------------------------------------------
#   fips_setup()
#   Performs one-time initialization of the build system. Must be called
#   at the start of the root CMakeLists.txt file.
#
macro(fips_setup)

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
    if (FIPS_DEPLOY_DIR)
        message("FIPS_DEPLOY_DIR: ${FIPS_DEPLOY_DIR}")
    else()
        message(FATAL_ERROR "Must specify absolute FIPS_DEPLOY_DIR before calling fips_setup()!")
    endif()
    message("FIPS_AUTO_IMPORT: ${FIPS_AUTO_IMPORT}")

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
        message("Detected C++ Compiler: Clang (FIPS_CLANG)")
    elseif (${CMAKE_CXX_COMPILER_ID} MATCHES "GNU")
        set(FIPS_GCC 1)
        message("Detected C++ Compiler: GCC (FIPS_GCC)")
    elseif (MSVC)
        set(FIPS_MSVC 1)
        message("Detected C++ Compiler: VStudio (FIPS_MSVC)")
    else()
        message("Detected C++ Compiler: Unknown")
    endif()

    # set FIPS_CONFIG to default if not provided by command line
    # (this provides better compatibility with some IDEs not directly
    # supported by cmake, like QtCreator or CLion
    if (NOT FIPS_CONFIG)
        message("FIPS_CONFIG not provided by command line, selecting default value")
        fips_choose_config()
    endif()
    message("FIPS_CONFIG: ${FIPS_CONFIG}")

    # Eclipse: Disable linked resources because Eclipse may get confused by these linked resources
    if (${CMAKE_GENERATOR} MATCHES "Eclipse CDT4")
        set(CMAKE_ECLIPSE_GENERATE_LINKED_RESOURCES OFF)
        set(CMAKE_ECLIPSE_GENERATE_SOURCE_PROJECT ON)
        set(CMAKE_ECLIPSE_VERSION "4.3" CACHE STRING "Eclipse version")
        set(CMAKE_CXX_COMPILER_ARG1 "-std=c++11" CACHE STRING "C++ version for Eclipse")
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

    # enable ccache??
    if (FIPS_USE_CCACHE)
        find_program(CCACHE "ccache")
        if (CCACHE)
            if (NOT FIPS_EMSCRIPTEN)
                message("Using ccache")
                set_property(GLOBAL PROPERTY RULE_LAUNCH_COMPILE ${CCACHE})
                set_property(GLOBAL PROPERTY RULE_LAUNCH_LINK ${CCACHE})
            else()
                message("ccache disabled on emscripten")
            endif()
        else()
            message(WARNING "ccache enabled but not found")
        endif()
    endif()

    # setup standard link directories
    fips_setup_link_directories()

    # setup the target group variable, used to group targets into folders in IDEs
    set_property(GLOBAL PROPERTY USE_FOLDERS ON)
    set(TARGET_GROUP "")

    # check whether python is installed
    find_program(PYTHON "python")
    if (NOT PYTHON)
        message(FATAL_ERROR "Python not found, required for code generation!")
    endif()

    # write empty target files (will be populated in the fips_end macros)
    fips_reset_targets_list()

    # initialize code generation
    fips_begin_gen()

    # load project-local fips-include.cmake if exists
    if (EXISTS "${FIPS_PROJECT_DIR}/fips-include.cmake")
        include("${FIPS_PROJECT_DIR}/fips-include.cmake")
    endif()

    # load generated .fips-imports.cmake if exists
    if (EXISTS "${FIPS_PROJECT_DIR}/.fips-imports.cmake")
        include("${FIPS_PROJECT_DIR}/.fips-imports.cmake")
    endif()

endmacro()

#-------------------------------------------------------------------------------
#   fips_finish()
#
macro(fips_finish)
    # nothing to do, reserved for future use
endmacro()

#-------------------------------------------------------------------------------
#   fips_ide_group(group)
#   Define the IDE group name for the following targets.
#
macro(fips_ide_group group)
    set(FIPS_TARGET_GROUP ${group})
endmacro()

#-------------------------------------------------------------------------------
#   fips_project(proj)
#   Starts a new project.
#
macro(fips_project proj)
    project(${proj})
endmacro()

#-------------------------------------------------------------------------------
#   fips_begin_module(module)
#   Begin defining an fips module.
#
macro(fips_begin_module name)
    set(name ${name})
    if (FIPS_CMAKE_VERBOSE)
        message("Module: name=" ${name})
    endif()
    fips_reset(${name})
endmacro()

#-------------------------------------------------------------------------------
#   fips_end_module(module)
#   End defining an fips module, the interesting stuff happens here.
#
macro(fips_end_module)

    # add library target
    add_library(${CurTargetName} ${CurSources})
    fips_apply_target_group(${CurTargetName})

    # set platform- and target-specific compiler options
    fips_vs_apply_options(${CurTargetName})

    # add dependencies
    fips_resolve_dependencies(${CurTargetName})

    # handle generators (post-target)
    fips_handle_generators(${CurTargetName})

    # record target name and type in the fips_targets.yml file
    fips_addto_targets_list(${CurTargetName} "module")

endmacro()

#-------------------------------------------------------------------------------
#   fips_begin_lib(name)
#   Begin defining a static link library
#
macro(fips_begin_lib name)
    set(name ${name})
    if (FIPS_CMAKE_VERBOSE)
        message("Library: name=" ${name})
    endif()
    fips_reset(${name})
endmacro()

#-------------------------------------------------------------------------------
#   fips_end_library(name)
#   End defining a static link library.
#
macro(fips_end_lib)

    # add library target
    add_library(${CurTargetName} ${CurSources})
    fips_apply_target_group(${CurTargetName})

    # set platform- and target-specific compiler options
    fips_vs_apply_options(${CurTargetName})
    
    # add dependencies
    fips_resolve_dependencies(${CurTargetName})

    # handle generators (post-target)
    fips_handle_generators(${CurTargetName})

    # record target name and type in the fips_targets.yml file
    fips_addto_targets_list(${CurTargetName} "lib")

endmacro()

#-------------------------------------------------------------------------------
#   fips_begin_app(name type)
#   Begin an fips command line app.
#   Type can be "windowed" or "cmdline", default is "cmdline".
#
macro(fips_begin_app name type)
    if (${type} STREQUAL "windowed" OR ${type} STREQUAL "cmdline")
        fips_reset(${name})
        set(CurAppType ${type})
        if (FIPS_CMAKE_VERBOSE)
            message("App: name=" ${CurTargetName} " type=" ${CurAppType})
        endif()
    else()
        message(FATAL_ERROR "type must be \"windowed\" or \"cmdline\"!")
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_end_app()
#   End defining an application.
#
macro(fips_end_app)

    # add standard frameworks and libs
    if (FIPS_OSX)
        fips_frameworks_osx(${FIPS_OSX_STANDARD_FRAMEWORKS})
    endif()

    if (NOT CurSources)
        message(FATAL_ERROR "No sources in target: ${CurTargetName} !!!")
    endif()

    # add executable target
    if (${CurAppType} STREQUAL "windowed")
        # a windowed application
        if (FIPS_OSX OR FIPS_IOS)
            add_executable(${CurTargetName} MACOSX_BUNDLE ${CurSources})
            fips_osx_add_target_properties(${CurTargetName})
            fips_copy_osx_dylib_files(${CurTargetName} 1)
        elseif (FIPS_WIN32 OR FIPS_WIN64)
            add_executable(${CurTargetName} WIN32 ${CurSources})
        elseif (FIPS_ANDROID)
            add_library(${CurTargetName} SHARED ${CurSources})
        else()
            add_executable(${CurTargetName} ${CurSources})
        endif()
    else()
        # a command line application
        if (FIPS_ANDROID)
            add_library(${CurTargetName} SHARED ${CurSources})
        else()
            add_executable(${CurTargetName} ${CurSources})
        endif()
        if (FIPS_OSX OR FIPS_IOS)
            fips_copy_osx_dylib_files(${CurTargetName} 0)
        endif()
    endif()
    fips_apply_target_group(${CurTargetName})

    # set platform- and target-specific compiler options
    fips_vs_apply_options(${CurTargetName})

    # android specific stuff
    if (FIPS_ANDROID)
        fips_android_create_project(${CurTargetName})
        fips_android_postbuildstep(${CurTargetName})
    endif()

    # handle generators (post-target)
    fips_handle_generators(${CurTargetName})

    # add dependencies
    fips_resolve_dependencies(${CurTargetName})

    # PNaCl specific stuff
    if (FIPS_PNACL)
        fips_pnacl_create_wrapper(${CurTargetName})
        fips_pnacl_post_buildsteps(${CurTargetName})
    endif()

    # setup executable output directory and postfixes (_debug, etc...)
    fips_config_output_directory(${CurTargetName})
    fips_config_postfixes_for_exe(${CurTargetName})

    # record target name and type in the fips_targets.yml file
    fips_addto_targets_list(${CurTargetName} "app")
endmacro()

#-------------------------------------------------------------------------------
#   fips_begin_sharedlib(name)
#   Begin a fips shared library.
#
macro(fips_begin_sharedlib name)
    fips_reset(${name})
    if (FIPS_CMAKE_VERBOSE)
        message("Shared Lib: name=" ${CurTargetName})
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_end_sharedlib()
#   End defining a shared library.
#
macro(fips_end_sharedlib)

    # add standard frameworks and libs
    if (FIPS_OSX)
        fips_frameworks_osx(${FIPS_OSX_STANDARD_FRAMEWORKS})
    endif()

    if (NOT CurSources)
        message(FATAL_ERROR "No sources in target: ${CurTargetName} !!!")
    endif()

    # add shared lib target
    add_library(${CurTargetName} SHARED ${CurSources})
    fips_apply_target_group(${CurTargetName})

    # set platform- and target-specific compiler options
    fips_vs_apply_options(${CurTargetName})

    # handle generators (post-target)
    fips_handle_generators(${CurTargetName})

    # add dependencies
    fips_resolve_dependencies(${CurTargetName})

    # setup executable output directory and postfixes (_debug, etc...)
    fips_config_output_directory(${CurTargetName})

    # record target name and type in the fips_targets.yml file
    fips_addto_targets_list(${CurTargetName} "sharedlib")

endmacro()

#-------------------------------------------------------------------------------
#   fips_deps(deps ...)
#   Add one or more dependencies to the current target. The dependencies
#   must be cmake build targets defined with fips_begin/end_module()
#   or fips_begin/end_lib(). Dependencies can also be added to fips modules
#   or libs, they will then be resolved recursively in the app linking stage.
#
macro(fips_deps deps)
    foreach(dep ${ARGV})
        list(APPEND CurDependencies ${dep})
    endforeach()
endmacro()

#-------------------------------------------------------------------------------
#   fips_libs(libs ...)
#   Add one or more static link library dependencies to the current target.
#   The current target can also be a fips module or lib. Dependencies added
#   with fips_libs() will be resolved recursively in the app linking stage
#   (see fips_deps()).
#
macro(fips_libs libs)
    foreach(lib ${ARGV})
        list(APPEND CurLinkLibs ${lib})
    endforeach()
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
        list(APPEND CurLinkLibsDebug ${lib})
    endforeach()
endmacro()

#-------------------------------------------------------------------------------
#   fips_libs_release(libs ...)
#   Same as fips_libs_debug(), but for release mode (or rather: all non-debug
#   modes).
#
macro(fips_libs_release libs)
    foreach(lib ${ARGV})
        list(APPEND CurLinkLibsRelease ${lib})
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
        # group is explicitely given as GROUP argument
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
#       [NO_RECURSE])
#
#   Add files from a path to the current target by using globbing expression.
#   It also creates and IDE group.
#
#   EXCEPT:   globbing expressions on files to exclude
#   GROUP:    the same as fips_dir GROUP, used for grouping files in a project
#   NO_RECURSE: do not use GLOB_RECURSE on globbing expressions
#
#   Note: fips_dir is used internally, so the current dir will change and you
#   will be able to more operation on this dir as fips_files().
#
macro(fips_files_ex path)
    set(options NO_RECURSE)
    set(oneValueArgs GROUP)
    set(multiValueArgs EXCEPT)
    CMAKE_PARSE_ARGUMENTS(_fd "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
    if (_fg_UNPARSED_ARGUMENTS)
        message(FATAL_ERROR "fips_files_ex(): called with invalid args '${_fg_UNPARSED_ARGUMENTS}'")
    endif()

    if (NOT _bs_GROUP)
        set(_bs_GROUP ".")
    else()
        #message(STATUS "Group: found ${_bs_GROUP}")
    endif()

    set(path "./${path}/")
    file(TO_CMAKE_PATH ${path} path)
    #message(STATUS "Path: ${path} - ${CMAKE_CURRENT_SOURCE_DIR}/${path}")

    set(ARG_LIST ${ARGV})
    list(REMOVE_AT ARG_LIST 0)
    #message(STATUS "ARGS: ${ARG_LIST}")

    set(_fd_FILE_LIST "")
    foreach (_fd_glob_expr ${ARG_LIST})
        #message(STATUS "Glob: ${path}/${_fd_glob_expr}")
        if (_fd_NO_RECURSE)
            file(GLOB _fd_TMP RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/${path} "${path}/${_fd_glob_expr}")
            #message(STATUS ${_fd_TMP})
        else()
            file(GLOB_RECURSE _fd_TMP RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/${path} "${path}/${_fd_glob_expr}")
            #message(STATUS ${_fd_TMP})
        endif()
        list(APPEND _fd_FILE_LIST ${_fd_TMP})
    endforeach()
    #message(STATUS "${_fd_FILE_LIST}")

    if (_fd_EXCEPT)
        set(_fd_EXCEPT_FILE_LIST "")
        foreach (_fd_glob_expr ${_fd_EXCEPT})
            #message(STATUS "Except Glob: ${path}/${_fd_glob_expr}")
            if (_fd_NO_RECURSE)
                file(GLOB _fd_TMP RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/${path} "${path}/${_fd_glob_expr}")
                #message(STATUS ${_fd_TMP})
            else()
                file(GLOB_RECURSE _fd_TMP RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}/${path} "${path}/${_fd_glob_expr}")
                #message(STATUS ${_fd_TMP})
            endif()
            list(APPEND _fd_EXCEPT_FILE_LIST ${_fd_TMP})
        endforeach()
        #message(STATUS "Remove: ${_fd_EXCEPT_FILE_LIST}")
        list(LENGTH _fd_EXCEPT_FILE_LIST _has_files)
        if (_has_files)
            list(REMOVE_ITEM _fd_FILE_LIST ${_fd_EXCEPT_FILE_LIST})
        endif()
    endif()
    #message(STATUS "Result: ${_fd_FILE_LIST}")

    fips_dir(${path} GROUP ${_fd_GROUP})
    fips_files(${_fd_FILE_LIST})
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
    set(oneValueArgs FROM TYPE SOURCE HEADER ARGS REQUIRES)
    set(multiValueArgs)
    CMAKE_PARSE_ARGUMENTS(_fg "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})
    if (_fg_UNPARSED_ARGUMENTS)
        message(FATAL_ERROR "fips_generate(): called with invalid args '${_fg_UNPARSED_ARGUMENTS}'")
    endif()
    if (NOT _fg_FROM)
        message(FATAL_ERROR "fips_generate(): FROM arg required")
    endif()
    if (NOT _fg_SOURCE AND NOT _fg_HEADER)
        # if both no SOURCE and no HEADER provided, set both
        # to input file plus .cc / .h extension
        get_filename_component(f_ext ${_fg_FROM} EXT)
        string(REPLACE ${f_ext} ".cc" _fg_SOURCE ${_fg_FROM})
        string(REPLACE ${f_ext} ".h" _fg_HEADER ${_fg_FROM})
    endif()
    if (_fg_REQUIRES)
        fips_add_target_dependency(${_fg_REQUIRES})
    endif()
    fips_add_file("${_fg_FROM}")
    fips_add_generator(${CurTargetName} "${_fg_TYPE}" ${_fg_OUT_OF_SOURCE} "${_fg_FROM}" "${_fg_SOURCE}" "${_fg_HEADER}" "${_fg_ARGS}") 
endmacro()

#-------------------------------------------------------------------------------
#   fips_add_subdirectory(dir)
#
macro(fips_add_subdirectory dir)
    add_subdirectory(${dir})
endmacro()

#-------------------------------------------------------------------------------
#   fips_include_directories(dir)
#
macro(fips_include_directories dir)
    foreach (cur_dir ${ARGV})
        include_directories(${cur_dir})
    endforeach()
endmacro()

