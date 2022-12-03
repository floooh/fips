#-------------------------------------------------------------------------------
#   fips_deprecated.cmake
#
#   Function wrappers with deprecation warnings.
#-------------------------------------------------------------------------------
macro(fips_project proj)
    message(WARNING "!!! DEPRECATED !!! fips_finish() is deprecated, use project()")
    project(${proj})
endmacro()

macro(fips_finish)
    message(WARNING "!!! DEPRECATED !!! fips_finish() is deprecated, please remove the call")
endmacro()

macro(fips_begin_module name)
    message(WARNING "!!! DEPRECATED !!! fips_begin_module() is deprecated, use fips_begin_lib()")
    fips_begin_lib(${name})
endmacro()

macro(fips_end_module)
    message(WARNING "!!! DEPRECATED !!! fips_end_module() is deprecated, use fips_end_lib()")
    fips_end_lib()
endmacro()

macro(fips_add_subdirectory dir)
    message(WARNING "!!! DEPRECATED !!! fips_add_subdirectory() is deprecated, use add_subdirectory()")
    add_subdirectory(${dir})
endmacro()

macro(fips_include_directories dir)
    message(WARNING "!!! DEPRECATED !!! fips_include_directories() is deprecated, use target_include_directories()")
    foreach (cur_dir ${ARGV})
        include_directories(${cur_dir})
    endforeach()
endmacro()
