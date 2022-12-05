#-------------------------------------------------------------------------------
#   fips_private.cmake
#   Private cmake macros (all the public stuff is in fips.cmake)
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#   fisit_reset(target)
#   Reset the global tracker variables.
#
macro(fips_reset target)
    set(CurDir)
    set(CurGroup "")
    set(CurTargetName ${target})
    set(FIPS_OSX_PLIST_PATH)
endmacro()

#-------------------------------------------------------------------------------
#   fips_apply_target_ide_group(target)
#   Apply IDE group name to target.
#
macro(fips_apply_target_ide_group target)
    if (NOT ${FIPS_TARGET_GROUP} STREQUAL "")
        set_target_properties(${target} PROPERTIES FOLDER ${FIPS_TARGET_GROUP})
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_setup_link_directories()
#   Setup the link library search paths.
#
macro(fips_setup_link_directories)
    if (EXISTS ${FIPS_PROJECT_DIR}/lib/${FIPS_PLATFORM_NAME})
        link_directories(${FIPS_PROJECT_DIR}/lib/${FIPS_PLATFORM_NAME})
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_config_postfixes_for_exe(target)
#   Internal macro to set the executable extensions
#
macro(fips_config_postfixes_for_exe target)
    if (FIPS_EMSCRIPTEN)
        set_target_properties(${target} PROPERTIES RELEASE_POSTFIX ${FIPS_EMSCRIPTEN_POSTFIX})
        set_target_properties(${target} PROPERTIES DEBUG_POSTFIX ${FIPS_EMSCRIPTEN_POSTFIX})
        set_target_properties(${target} PROPERTIES PROFILING_POSTFIX ${FIPS_EMSCRIPTEN_POSTFIX})
    elseif (FIPS_WASISDK)
        set_target_properties(${target} PROPERTIES RELEASE_POSTFIX ${FIPS_WASISDK_POSTFIX})
        set_target_properties(${target} PROPERTIES DEBUG_POSTFIX ${FIPS_WASISDK_POSTFIX})
        set_target_properties(${target} PROPERTIES PROFILING_POSTFIX ${FIPS_WASISDK_POSTFIX})
    endif()
endmacro(fips_config_postfixes_for_exe)

#-------------------------------------------------------------------------------
#   fips_output_directory(target)
#   Internal macro to set the output directory for exes and sharedlibs
#
function(fips_config_output_directory target)
    if (NOT FIPS_ANDROID)
        set(dir ${FIPS_PROJECT_DEPLOY_DIR})

        # exes
        set_target_properties(${target} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${dir})
        set_target_properties(${target} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_RELEASE ${dir})
        set_target_properties(${target} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_DEBUG ${dir})
        set_target_properties(${target} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_PROFILING ${dir})

        # ...and DLLs
        set_target_properties(${target} PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${dir})
        set_target_properties(${target} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_RELEASE ${dir})
        set_target_properties(${target} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_DEBUG ${dir})
        set_target_properties(${target} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_PROFILING ${dir})
    endif()
endfunction()

#-------------------------------------------------------------------------------
#   fips_init_targets_list()
#   Clears a .yml file which keeps track of all targets.
#
function(fips_init_targets_list)
    file(WRITE "${CMAKE_BINARY_DIR}/fips_targets.yml" "---\n")
endfunction()

#-------------------------------------------------------------------------------
#   fips_add_to_targets_list(target type)
#   Adds a new entry to the targets type list, this is called from
#   the fips_end_xxx() functions.
#
function(fips_add_to_targets_list target type)
    file(APPEND "${CMAKE_BINARY_DIR}/fips_targets.yml" "${target} : ${type}\n")
endfunction()

#-------------------------------------------------------------------------------
#   fips_choose_config()
#   Sets the FIPS_CONFIG variable to a sensible value, call this if
#   FIPS_CONFIG hasn't been provided by the command line when using
#   some IDEs which are not directly supported by cmake, like QtCreator
#   or CLion.
#
macro(fips_choose_config)
    if (FIPS_HOST_WINDOWS)
        if (CMAKE_CL_64)
            if (${CMAKE_BUILD_TYPE} AND ${CMAKE_BUILD_TYPE} STREQUAL "Release")
                set(FIPS_CONFIG "win64-vstudio-release")
            elseif (${CMAKE_BUILD_TYPE} AND ${CMAKE_BUILD_TYPE} STREQUAL "Profiling")
                set (FIPS_CONFIG "win64-vstudio-profiling")
            else()
                set (FIPS_CONFIG "win64-vstudio-debug")
            endif()
        else()
            if (${CMAKE_BUILD_TYPE} AND ${CMAKE_BUILD_TYPE} STREQUAL "Release")
                set (FIPS_CONFIG "win32-vstudio-release")
            elseif (${CMAKE_BUILD_TYPE} AND ${CMAKE_BUILD_TYPE} STREQUAL "Profiling")
                set (FIPS_CONFIG "win32-vstudio-profiling")
            else()
                set (FIPS_CONFIG "win32-vstudio-debug")
            endif()
        endif()
    elseif (FIPS_HOST_OSX)
        if (${CMAKE_BUILD_TYPE} AND ${CMAKE_BUILD_TYPE} STREQUAL "Release")
            set (FIPS_CONFIG "osx-make-release")
        elseif (${CMAKE_BUILD_TYPE} AND ${CMAKE_BUILD_TYPE} STREQUAL "Profiling")
            set (FIPS_CONFIG "osx-make-profiling")
        else()
            set (FIPS_CONFIG "osx-make-debug")
        endif()
    elseif (FIPS_HOST_LINUX)
        if (${CMAKE_BUILD_TYPE} AND ${CMAKE_BUILD_TYPE} STREQUAL "Release")
            set (FIPS_CONFIG "linux-make-release")
        elseif (${CMAKE_BUILD_TYPE} AND ${CMAKE_BUILD_TYPE} STREQUAL "Profiling")
            set (FIPS_CONFIG "linux-make-profiling")
        else()
            set (FIPS_CONFIG "linux-make-debug")
        endif()
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_add_file()
#   Private helper function to add a single file to the project, with
#   additional handling for code generation files.
#
macro(fips_add_file new_file)

    # handle subdirectory
    if (CurDir)
        set(cur_file "${CurDir}${new_file}")
    else()
        set(cur_file ${new_file})
    endif()
    # NOTE: this should be LAST_EXT, but that's only supported since cmake 3.14
    get_filename_component(f_ext ${cur_file} EXT)

    # determine source group name and
    # add to current source group
    source_group("${CurGroup}" FILES ${cur_file})

    if (FIPS_OSX)
        # handle plist files special
        if ("${f_ext}" STREQUAL ".plist")
            set(FIPS_OSX_PLIST_PATH "${CMAKE_CURRENT_SOURCE_DIR}/${cur_file}")
        endif()
    endif()

    # add to target sources
    target_sources(${CurTargetName} PRIVATE ${cur_file})
endmacro()

#-------------------------------------------------------------------------------
#   fips_dir_groups()
#   Private helper function to add a list of files in a directory tree as groups
#   emulating the directory tree.
#
macro(fips_dir_groups path files)
    foreach (_fd_file ${files})
        get_filename_component(_fd_dir "${_fd_file}" DIRECTORY)
        get_filename_component(_fd_name "${_fd_file}" NAME)
        if ("${path}" STREQUAL ".")
            if ("${_fd_dir}" STREQUAL "")
                fips_dir(".")
            else()
                fips_dir("${_fd_dir}") # otherise it may end as "./" and create a group "."
            endif()
        else()
            fips_dir("${path}/${_fd_dir}")
        endif()
        fips_add_file(${_fd_name} ".py" "NO_GENERATOR" "NO_GENFILES")
    endforeach()
endmacro()

#-------------------------------------------------------------------------------
#   fips_add_target_dependency(target...)
#   Add one or more dependencies to the current target. The dependencies
#   must be cmake build targets defined with fips_begin*/fips_end*().
#   Used to define a build order required when, for example, building tools to
#   use during compilation of the current target.
#
macro(fips_add_target_dependency targets)
    foreach(target ${ARGV})
        if (TARGET ${target})
            list(APPEND CurTargetDependencies ${target})
        endif()
    endforeach()
    if (CurTargetDependencies)
        list(REMOVE_DUPLICATES CurTargetDependencies)
    endif()
endmacro()
