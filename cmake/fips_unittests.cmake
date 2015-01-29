#-------------------------------------------------------------------------------
#   fips_unittests.cmake
#
#   Macros for generating unit tests.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#   fips_begin_unittest(name)
#   Begin defining a unit test.
#
macro(fips_begin_unittest name)
    if (FIPS_UNITTESTS)
        set(CurTargetName ${name}Test)
        set(FipsAddFilesEnabled 1)
        fips_reset(${CurTargetName})
        if (FIPS_OSX)
            set(CurAppType "windowed")
        else()
            set(CurAppType "cmdline")
        endif()
    else()
        set(FipsAddFilesEnabled)
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_end_unittest()
#   End defining a unittest named 'name' from sources in 'dir'
#
macro(fips_end_unittest)
    
    if (FIPS_UNITTESTS)

        if (FIPS_CMAKE_VERBOSE)
            message("Unit Test: name=" ${CurTargetName})
        endif()
    
        # FIXME: add unittestpp lib dependency
        fips_deps(unittestpp)

        # FIXME: generate a scratch main-source-file
        set(main_path ${CMAKE_CURRENT_BINARY_DIR}/${CurTargetName}_main.cc)
        file(WRITE ${main_path}
            "// machine generated, do not edit\n"
            "#include \"Pre.h\"\n"
            "#include \"Core/Core.h\"\n"
            "#include \"UnitTest++/src/UnitTest++.h\"\n"
            "int main(void) {\n"
            "    Oryol::Core::Setup();\n"
            "    int res = UnitTest::RunAllTests();\n"
            "    Oryol::Core::Discard();\n"
            "    return res;\n"
            "}\n"
        )

        # generate a command line app
        list(APPEND CurSources ${main_path})
        fips_end_app()
        set_target_properties(${CurTargetName} PROPERTIES FOLDER "UnitTests")

        # add as cmake unit test
        add_test(NAME ${CurTargetName} COMMAND ${CurTargetName})

        # if configured, start the app as post-build-step
        if (FIPS_UNITTESTS_RUN_AFTER_BUILD)
            add_custom_command (TARGET ${CurTargetName} POST_BUILD COMMAND ${CurTargetName})
        endif()
    endif()
    set(FipsAddFilesEnabled 1)
endmacro()

