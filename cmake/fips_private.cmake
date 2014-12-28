#-------------------------------------------------------------------------------
#   fips_private.cmake
#   Private cmake macros (all the public stuff is in fips.cmake)
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#   fisit_reset(target)
#   Reset the global tracker variables.
#
macro(fips_reset target)
    set(CurSources)
    set(CurPyFiles)
    set(CurDependencies)
    set(CurLinkLibs)
    set(CurFrameworks)
    set(CurModuleName)
    set(CurLibraryName)
    set(CurAppName)
    set(CurAppType)
    set(CurImgFiles)
endmacro()

#-------------------------------------------------------------------------------
#   fips_apply_target_group(target)
#   Apply IDE group name to target.
#
macro(fips_apply_target_group target)
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
#   fips_recurse_deps(input output)
#
macro(fips_recurse_deps input output)
    list(APPEND ${output} ${input})
    get_property(sub_input GLOBAL PROPERTY ${input}_deps)
    foreach(dep ${sub_input})
        fips_recurse_deps(${dep} ${output})
    endforeach()
endmacro()

#-------------------------------------------------------------------------------
#   fips_resolve_dependencies(target)
#   Recursively resolve dependencies of a target.
#
macro(fips_resolve_dependencies target)
    set(resolvedDeps)
    get_property(input GLOBAL PROPERTY ${target}_deps)
    foreach(dep ${input})
        fips_recurse_deps(${dep} resolvedDeps)
    endforeach()

# NOTE: we do NOT remove dups, this simplifies the tricky linker order
# requirements on GCC
# FIXME: there must be a more elegant way...
#    if (resolvedDeps)
#       list(REMOVE_DUPLICATES resolvedDeps)
#    endif()
    if (FIPS_CMAKE_VERBOSE)
        message("${target} Dependencies: ${resolvedDeps}")
    endif()
    target_link_libraries(${target} ${resolvedDeps})
endmacro()

#-------------------------------------------------------------------------------
#   fips_recurse_libs(input output)
#
macro(fips_recurse_libs input output)
    list(APPEND ${output} ${input})
    get_property(sub_input GLOBAL PROPERTY ${input}_libs)
    foreach(lib ${sub_input})
        fips_recurse_libs(${lib} ${output})
    endforeach()
endmacro()

#-------------------------------------------------------------------------------
#   fips_resolve_linklibs(target)
#   Recursively resolve link-libs of a target.
#
macro(fips_resolve_linklibs target)
    set(resolvedLibs)
    get_property(input GLOBAL PROPERTY ${target}_libs)
    foreach(lib ${input})
        fips_recurse_libs(${lib} resolvedLibs)
    endforeach()
    if (resolvedLibs)
       list(REMOVE_DUPLICATES resolvedLibs)
    endif()
    if (FIPS_CMAKE_VERBOSE)
        message("${target} Libs: ${resolvedLibs}")
    endif()
    target_link_libraries(${target} ${resolvedLibs})
endmacro()

#-------------------------------------------------------------------------------
#   fips_config_postfixes_for_exe(target)
#   Internal macro to set the executable extensions
#
macro(fips_config_postfixes_for_exe target)
    if (NOT FIPS_ANDROID)
        if (FIPS_EMSCRIPTEN)
            set_target_properties(${target} PROPERTIES RELEASE_POSTFIX .html)
            set_target_properties(${target} PROPERTIES DEBUG_POSTFIX .html)
            set_target_properties(${target} PROPERTIES PROFILING_POSTFIX .html)
        elseif (FIPS_PNACL)
            set_target_properties(${target} PROPERTIES RELEASE_POSTFIX .pexe)
            set_target_properties(${target} PROPERTIES DEBUG_POSTFIX .pexe)
            set_target_properties(${target} PROPERTIES PROFILING_POSTFIX .pexe)
        endif()
    endif()
endmacro(fips_config_postfixes_for_exe)

#-------------------------------------------------------------------------------
#   fips_exe_output_directory(target)
#   Internal macro to set the output directory
#
function(fips_exe_output_directory target)
    if (NOT (FIPS_IOS OR FIPS_ANDROID))
        set(dir ${FIPS_DEPLOY_DIR}/${CMAKE_PROJECT_NAME}/${FIPS_CONFIG})

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

