#-------------------------------------------------------------------------------
#   fips.cmake
#   Main cmake header for fips, this must be included in the top-level
#   CMakeLists.txt file of a fips project
#-------------------------------------------------------------------------------
get_filename_component(FIPS_PROJECT_DIR "." ABSOLUTE)
get_filename_component(FIPS_DEPLOY_DIR "../fips-deploy" ABSOLUTE)

include(CMakeParseArguments)

include("${FIPS_ROOT_DIR}/cmake/fips_private.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_unittests.cmake")
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
option(FIPS_ALLOCATOR_DEBUG "Enable allocator debugging code (slow)" OFF)
option(FIPS_COMPILE_VERBOSE "Enable very verbose compilation" OFF)
option(FIPS_USE_CCACHE "Enable ccache when building with gcc or clang" OFF)

# turn some dependent options on/off
if (FIPS_UNITTESTS)
    enable_testing()
    set(FIPS_EXCEPTIONS ON CACHE BOOL "Enable C++ exceptions" FORCE)
else()
    set(FIPS_EXCEPTIONS OFF CACHE BOOL "Enable C++ exceptions" FORCE)
endif()

#-------------------------------------------------------------------------------
#   fips_setup()
#   Performs one-time initialization of the build system. Must be called
#   at the start of the root CMakeLists.txt file.
#
macro(fips_setup)

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

    # set FIPS_CONFIG to default if not provided by command line
    # (this provides better compatibility with some IDEs not directly 
    # supported by cmake, like QtCreator or CLion
    if (NOT FIPS_CONFIG)
        message("FIPS_CONFIG not provided by command line, selecting default value")
        fips_choose_config()
    endif()
    message("FIPS_CONFIG: ${FIPS_CONFIG}")

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
    set(FIPS_IMPORT 1)
    if (EXISTS "${FIPS_PROJECT_DIR}/.fips-imports.cmake")
        include("${FIPS_PROJECT_DIR}/.fips-imports.cmake")
    endif()
    set(FIPS_IMPORT)

endmacro()

#-------------------------------------------------------------------------------
#   fips_finish()
#
macro(fips_finish)
    # FIXME!
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
    
    # setup dependency tracker variables for this module, executable
    # targets use this to resolve their dependencies
    set_property(GLOBAL PROPERTY ${CurTargetName}_deps ${CurDependencies})
    set_property(GLOBAL PROPERTY ${CurTargetName}_libs ${CurLinkLibs})
    set_property(GLOBAL PROPERTY ${CurTargetName}_frameworks ${CurFrameworks})

    # add library target
    add_library(${CurTargetName} ${CurSources})
    fips_apply_target_group(${CurTargetName})

    # make sure dependencies are built first
    if (CurDependencies)
        add_dependencies(${CurTargetName} ${CurDependencies})
    endif()

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

    # setup dependency tracker variables for this module, executable
    # targets use this to resolve their dependencies
    set_property(GLOBAL PROPERTY ${CurTargetName}_deps ${CurDependencies})
    set_property(GLOBAL PROPERTY ${CurTargetName}_libs ${CurLinkLibs})
    set_property(GLOBAL PROPERTY ${CurTargetName}_frameworks ${CurFrameworks})

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

    # android specific stuff
    if (FIPS_ANDROID)
        fips_android_create_project(${CurTargetName})
        fips_android_postbuildstep(${CurTargetName})
    endif()

    # handle generators (post-target)
    fips_handle_generators(${CurTargetName})

    # PNaCl specific stuff
    if (FIPS_PNACL)
        fips_pnacl_create_wrapper(${CurTargetName})
        fips_pnacl_post_buildsteps(${CurTargetName})
    endif()

    # add dependencies for target
    fips_resolve_dependencies(${CurTargetName})
    fips_resolve_linklibs(${CurTargetName})
    if (FIPS_OSX OR FIPS_IOS)
        fips_osx_resolve_frameworks(${CurTargetName})
    endif()

    # setup executable output directory and postfixes (_debug, etc...)
    fips_exe_output_directory(${CurTargetName})    
    fips_config_postfixes_for_exe(${CurTargetName})

    # record target name and type in the fips_targets.yml file
    fips_addto_targets_list(${CurTargetName} "app")

endmacro()

#-------------------------------------------------------------------------------
#   fips_deps(deps ...)
#   Add one or more dependencies to the current target.
#
macro(fips_deps deps)
    foreach(dep ${ARGV})
        list(APPEND CurDependencies ${dep})
    endforeach()    
endmacro()

#-------------------------------------------------------------------------------
#   fips_libs(libs ...)
#   Add one or more link libraries to the current target.
#
macro(fips_libs libs)
    foreach(lib ${ARGV})
        list(APPEND CurLinkLibs ${lib})
    endforeach()
endmacro()

#-------------------------------------------------------------------------------
#   fips_dir(dir)
#   Enter a source code subdirectory.
#
macro(fips_dir dir)
    if (${dir} STREQUAL ".")
        set(CurDir)
    else()
        set(CurDir "${dir}/")
    endif()
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
#   fips_generate(FROM input_file
#       [TYPE generator_type]
#       [SOURCE output_source]
#       [HEADER output_header])
#
#   Generic one C/C++ source/header pair from an input definition file
#   by running a python generator script.
#
#   FROM:   name of an input file to be processed 
#   TYPE:   the generator type, filename of a generator script with the .py
#   SOURCE: name of generated source file
#   HEADER: name of generated header file
#
#   If no TYPE is provided, the input_file must be a python script.
#
#   If both SOURCE and HEADER are omitted, it is assumed that the
#   generator script generated a input_file.cc/input_file.h pair.
#   Omitting one of SOURCE or HEADER means the generator script
#   will only generate either the SOURCE or HEADER file.
#
macro(fips_generate)
    set(options)
    set(oneValueArgs FROM TYPE SOURCE HEADER)
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
    fips_get_groupname(group_name)
    fips_add_file("${_fg_FROM}")
    fips_add_generator("${group_name}" "${_fg_TYPE}" "${_fg_FROM}" "${_fg_SOURCE}" "${_fg_HEADER}")
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

