#-------------------------------------------------------------------------------
#   fips_windows.cmake
#   Windows/VStudio-specific helper functions
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#   fips_vs_warning_level(1..4)
#   Set a module-specific warning level for Visual Studio, simply set this
#   within a 'begin/end' pair.
#
macro(fips_vs_warning_level level)
    if (FIPS_MSVC)
        set(CurCompileFlags "${CurCompileFlags} /W${level}")
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_vs_disable_warning(warnings ...)
#   Disable a specific vstudio warning
#
macro(fips_vs_disable_warnings warnings)
    if (FIPS_MSVC)
        foreach (warning ${ARGV})
            set(CurCompileFlags "${CurCompileFlags} /wd${warning}")
        endforeach()
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_vs_apply_options()
#   Applies the module-specific options set between begin/end
#
macro(fips_vs_apply_options target)
    if (FIPS_MSVC)
        if (NOT ${CurCompileFlags} STREQUAL "")
            set_target_properties(${target} PROPERTIES COMPILE_FLAGS ${CurCompileFlags})
        endif()
    endif()
endmacro()
