#-------------------------------------------------------------------------------
#   fips.cmake
#   Main cmake header for fips, this must be included in the top-level
#   CMakeLists.txt file of a fips project
#-------------------------------------------------------------------------------
get_filename_component(FIPS_PROJECT_DIR "." ABSOLUTE)
get_filename_component(FIPS_DEPLOY_DIR "../.fips-deploy" ABSOLUTE)

include("${FIPS_ROOT_DIR}/cmake/fips_private.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_unittests.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_android.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_osx.cmake")
include("${FIPS_ROOT_DIR}/cmake/fips_pnacl.cmake")
#include("${FIPS_ROOT_DIR}/cmake/fips_generators.cmake")

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
    if (FIPS_CONFIG)
        message("FIPS_CONFIG: ${FIPS_CONFIG}")
    else()
        message(FATAL_ERROR "Must provide -DFIPS_CONFIG='config-name' on command line!")
    endif()

    # set host system variables
    set (FIPS_HOST_WIN32 0)
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
    endif()

    # manually include "toolchain" files for non-crosscompiling scenarios
    if (NOT CMAKE_TOOLCHAIN_FILE)
        if (WIN32)
            include(${FIPS_ROOT_DIR}/cmake-toolchains/windows.cmake)
        elseif (APPLE)
            include(${FIPS_ROOT_DIR}/cmake-toolchains/osx.cmake)
        else()
            include(${FIPS_ROOT_DIR}/cmake-toolchains/linux.cmake)
        endif()
    endif()
    message("FIPS_PLATFORM: " ${FIPS_PLATFORM})

    # setup standard link directories
    fips_setup_link_directories()

    # setup the target group variable, used to group targets into folders in IDEs
    set_property(GLOBAL PROPERTY USE_FOLDERS ON)
    set(TARGET_GROUP "")
    
    # various global defines
    if (FIPS_ALLOCATOR_DEBUG)
        add_definitions(-DFIPS_ALLOCATOR_DEBUG=1)
    else()
        add_definitions(-DFIPS_ALLOCATOR_DEBUG=0)
    endif()
    if (FIPS_UNITTESTS)
        add_definitions(-DFIPS_UNITTESTS=1)
        if (FIPS_UNITTESTS_HEADLESS)
            add_definitions(-DFIPS_UNITTESTS_HEADLESS=1)
        else()
            add_definitions(-DFIPS_UNITTESTS_HEADLESS=0)
        endif()
    else()
        add_definitions(-DFIPS_UNITTESTS=0)
    endif()
    if (FIPS_NO_ASSERTS_IN_RELEASE)
        add_definitions(-DFIPS_NO_ASSERT=1)
    else()
        add_definitions(-DFIPS_NO_ASSERT=0)
    endif()

    # check whether python is installed
    find_program(PYTHON "python")
    if (PYTHON)
        message("PYTHON INTERPRETER FOUND")
    else()
        message("PYTHON INTERPRETER NOT FOUND, NO SOURCE CODE GENERATION!")
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
    set(CurModuleName ${name})
endmacro()

#-------------------------------------------------------------------------------
#   fips_end_module(module)
#   End defining an fips module, the interesting stuff happens here.
#
macro(fips_end_module)
    
    # setup dependency tracker variables for this module, executable
    # targets use this to resolve their dependencies
    set_property(GLOBAL PROPERTY ${CurModuleName}_deps ${CurDependencies})
    set_property(GLOBAL PROPERTY ${CurModuleName}_libs ${CurLinkLibs})
    set_property(GLOBAL PROPERTY ${CurModuleName}_frameworks ${CurFrameworks})

    # handle generators (pre-target)
    if (CurPyFiles)
        fips_handle_py_files_pretarget("${CurPyFiles}")
    endif()

    # add library target
    add_library(${CurModuleName} ${CurSources})
    fips_apply_target_group(${CurModuleName})

    # handle generators (post-target)
    if (CurPyFiles)
        fips_handle_py_files_posttarget(${CurModuleName} "${CurPyFiles}")
    endif()

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
    set(CurLibraryName ${name})
endmacro()

#-------------------------------------------------------------------------------
#   fips_end_library(name)
#   End defining a static link library.
#
macro(fips_end_lib)
    # add library target
    add_library(${CurLibraryName} ${CurSources})
    fips_apply_target_group(${CurLibraryName})
endmacro()

#-------------------------------------------------------------------------------
#   fips_begin_app(name type)
#   Begin an fips command line app.
#   Type can be "windowed" or "cmdline", default is "cmdline".
#
macro(fips_begin_app name type)
    if (${type} STREQUAL "windowed" OR ${type} STREQUAL "cmdline")
        fips_reset(${name})
        set(CurAppName ${name})
        set(CurAppType ${type})
        if (FIPS_CMAKE_VERBOSE)
            message("App: name=" ${CurAppName} " type=" ${CurAppType})
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
    set_property(GLOBAL PROPERTY ${CurAppName}_deps ${CurDependencies})
    set_property(GLOBAL PROPERTY ${CurAppName}_libs ${CurLinkLibs})
    set_property(GLOBAL PROPERTY ${CurAppName}_frameworks ${CurFrameworks})

    if (NOT CurSources)
        message(FATAL_ERROR "No sources in target: ${CurAppName} !!!")
    endif()

    # handle generators (pre-target)
    if (CurPyFiles)
        fips_handle_py_files_pretarget("${CurPyFiles}")
    endif()

    # add executable target
    if (${CurAppType} STREQUAL "windowed")
        # a windowed application 
        if (FIPS_OSX OR FIPS_IOS)
            add_executable(${CurAppName} MACOSX_BUNDLE ${CurSources})
            fips_osx_add_target_properties(${CurAppName})
            fips_copy_osx_dylib_files(${CurAppName} 1)
        elseif (FIPS_WIN32 OR FIPS_WIN64)
            add_executable(${CurAppName} WIN32 ${CurSources})
        elseif (FIPS_ANDROID)
            add_library(${CurAppName} SHARED ${CurSources})
        else()
            add_executable(${CurAppName} ${CurSources})
        endif()
    else()
        # a command line application
        if (FIPS_ANDROID)
            add_library(${CurAppName} SHARED ${CurSources})
        else()
            add_executable(${CurAppName} ${CurSources})
        endif()
        if (FIPS_OSX OR FIPS_IOS)
            fips_copy_osx_dylib_files(${CurAppName} 0)
        endif()
    endif()
    fips_apply_target_group(${CurAppName})

    # android specific stuff
    if (FIPS_ANDROID)
        fips_android_create_project(${CurAppName})
        fips_android_postbuildstep(${CurAppName})
    endif()

    # handle generators (post-target)
    if (CurPyFiles)
        fips_handle_py_files_posttarget(${CurAppName} "${CurPyFiles}")
    endif()

    # PNaCl specific stuff
    if (FIPS_PNACL)
        fips_pnacl_create_wrapper(${CurAppName})
        fips_pnacl_post_buildsteps(${CurAppName})
    endif()

    # add dependencies for target
    fips_resolve_dependencies(${CurAppName})
    fips_resolve_linklibs(${CurAppName})
    if (FIPS_OSX OR FIPS_IOS)
        fips_osx_resolve_frameworks(${CurAppName})
    endif()

    # setup executable output directory and postfixes (_debug, etc...)
    fips_exe_output_directory(${CurAppName})    
    fips_config_postfixes_for_exe(${CurAppName})

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
#   fips_sources(dirs ...)
#   Parse one or more directories for sources and add them to the current
#   target.
#
macro(fips_sources dirs)
    foreach (dir ${ARGV})
        # gather files
        file(GLOB src ${dir}/*.cc ${dir}/*.cpp ${dir}/*.c ${dir}/*.m ${dir}/*.mm ${dir}/*.h ${dir}/*.hh)
        file(GLOB pys ${dir}/*.py)
        file(GLOB shds ${dir}/*.shd)
        file(GLOB imgs ${dir}/*.png ${dir}/*.tga ${dir}/*.jpg)

        # determine group folder name
        string(REPLACE / \\ groupName ${dir})
        if (${dir} STREQUAL .)
            source_group("" FILES ${src} ${pys} ${shds} ${imgs})
        else()
            source_group(${groupName} FILES ${src} ${pys} ${shds} ${imgs})
        endif()

        # add generated source files
        foreach(py ${pys})
            string(REPLACE .py .cc pySrc ${py})
            string(REPLACE .py .h pyHdr ${py})
            list(APPEND CurSources ${pySrc} ${pyHdr})
            if (${dir} STREQUAL .)
                source_group("" FILES ${pySrc} ${pyHdr})
            else()
                source_group(${groupName} FILES ${pySrc} ${pyHdr})
            endif()
        endforeach()

        # add to global tracker variables
        list(APPEND CurSources ${src} ${pys} ${shds} ${imgs})
        list(APPEND CurPyFiles ${pys})

        # remove duplicate sources 
        if (CurSources)
            list(REMOVE_DUPLICATES CurSources)
        endif()

    endforeach()
endmacro()

#-------------------------------------------------------------------------------
#   fips_sources_posix(dirs ...)
#   Add POSIX specific sources.
#
macro(fips_sources_posix dirs)
    if (FIPS_POSIX)
        fips_sources(${ARGV})
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_sources_linux(dirs ...)
#   Add Linux specific sources.
#-------------------------------------------------------------------------------
macro(fips_sources_linux dirs)
    if (FIPS_LINUX)
        fips_sources(${ARGV})
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_sources_windows(dirs ...)
#   Add Windows specific sources.
#
macro(fips_sources_windows dirs)
    if (FIPS_WINDOWS)
        fips_sources(${ARGV})
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_sources_osx(dirs ...)
#   Add OSX specific sources (iOS or MacOS)
#-------------------------------------------------------------------------------
macro(fips_sources_osx dirs)
    if (FIPS_OSX)
        fips_sources(${ARGV})
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_sources_emscripten(dirs ...)
#   Add emscripten specific sources.
#-------------------------------------------------------------------------------
macro(fips_sources_emscripten dirs)
    if (FIPS_EMSCRIPTEN)
        fips_sources(${ARGV})
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_sources_pnacl(dirs ...)
#   Add PNACL specific sources.
#-------------------------------------------------------------------------------
macro(fips_sources_pnacl dirs)
    if (FIPS_PNACL)
        fips_sources(${ARGV})
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_sources_android(dirs ...)
#   Add Android specific sources.
#-------------------------------------------------------------------------------
macro(fips_sources_android dirs)
    if (FIPS_ANDROID)
        fips_sources(${ARGV})
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_sources_ios(dirs ...)
#   Add IOS specific sources.
#-------------------------------------------------------------------------------
macro(fips_sources_ios dirs)
    if (FIPS_IOS)
        fips_sources(${ARGV})
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_add_subdirectory(dir)
#
macro(fips_add_subdirectory dir)
    add_subdirectory(${dir})
endmacro()

