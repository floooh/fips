#-------------------------------------------------------------------------------
#   fips_generators.cmake
#   Helper cmake functions for integrating python generator scripts into 
#   the build process.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#   Background Info
#
#   There are 2 types of code generation:
#   (1) Just list a python file as source file, this file will be called
#       during the build and is expected to build exactly one .cc and one .h
#       file (this detail may change in the future).
#   (2) Or use the fips_generate() macro which accepts the name of a generator
#       python script (located under project-dir/fips-files/generators),
#       one input file, and a one or multiple output files. The generator
#       must produce the output files using the input file.
#
#   - all filenames handed to the generator scripts will be absolute paths
#   - the generator script must not overwrite the output files if they
#     are already uptodate to prevent triggering dependent targets
#
#   During a cmake run, one .yml file and one cmake custom target 
#   will be generated per compile target which needs code generation, 
#   the custom target will call a generated python file .fips-gen.py 
#   in the project root (created during 'fips gen') which takes
#   a generator.yml file as input and calls the listed generator, which 
#   in turn write the generated source file (after making sure that they 
#   are actually dirty). cmake will also setup a target dependency between
#   the generator target and the actual compile target which depends on the
#   generated source files.
#

#-------------------------------------------------------------------------------
#   fips_begin_gen(target)
#
#   Called from fips_begin_module, fips_begin_lib, fips_begin_app to 
#   clear the generator .yml file.
#
macro(fips_begin_gen)
    file(REMOVE "${CMAKE_BINARY_DIR}/fips_codegen.yml")
    set(CurProjectHasCodeGen)
endmacro()

#-------------------------------------------------------------------------------
#   fips_add_generator()
#   Add a code generator item to the current target.
#
macro(fips_add_generator target in_generator in_outofsource in_file out_src out_hdr args)
    if (FipsAddFilesEnabled)
        get_filename_component(f_abs ${CurDir}${in_file} ABSOLUTE)
        get_filename_component(f_dir ${f_abs} PATH)
        if ("${in_generator}" STREQUAL "")
            # special case: input file is the generator script
            set(generator ${f_abs})
        else()
            # add .py extension to generator type
            set(generator "${in_generator}.py")
        endif()
        set(yml_content "- generator: ${generator}\n  in: '${f_abs}'\n")
        if ("${out_src}" STREQUAL "")
            set(yml_content "${yml_content}  out_src: null\n")
        else()
            if (${in_outofsource}) 
                set(out_src_abs "${CMAKE_CURRENT_BINARY_DIR}/${out_src}")
            else()
                set(out_src_abs "${f_dir}/${out_src}")
            endif()
            list(APPEND CurSources ${out_src_abs})
            source_group("${CurGroup}\\gen" FILES ${out_src_abs})
            set(yml_content "${yml_content}  out_src: '${out_src_abs}'\n")
            if (NOT EXISTS ${out_src_abs})
                file(WRITE ${out_src_abs} " ")
            endif()
        endif()
        if ("${out_hdr}" STREQUAL "")
            set(yml_content "${yml_content}  out_hdr: null\n")
        else()
            if (${in_outofsource})
                set(out_hdr_abs "${CMAKE_CURRENT_BINARY_DIR}/${out_hdr}")
            else()
                set(out_hdr_abs "${f_dir}/${out_hdr}")
            endif()
            list(APPEND CurSources ${out_hdr_abs})
            source_group("${CurGroup}\\gen" FILES ${out_hdr_abs})
            set(yml_content "${yml_content}  out_hdr: '${out_hdr_abs}'\n")
            if (NOT EXISTS ${out_hdr_abs})
                file(WRITE ${out_hdr_abs} " ")
            endif()
        endif()
        if (NOT ${args} STREQUAL "")
            set(yml_content "${yml_content}  args: ${args}\n")
        endif()

        # write 'environment'
        set(yml_content "${yml_content}  env:\n")
        set(yml_content "${yml_content}    target_platform: '${FIPS_PLATFORM_NAME}'\n")

        file(APPEND "${CMAKE_BINARY_DIR}/fips_codegen.yml" "${yml_content}")
        
        # if generated out-of-source, add the current build dir to
        # the header search path, only for the current directory
        if (${in_outofsource})
            include_directories(${CMAKE_CURRENT_BINARY_DIR})
        endif()
        set(CurProjectHasCodeGen 1)
    endif()
endmacro()
            
#-------------------------------------------------------------------------------
#   fips_handle_py_files_posttarget(target pyFiles)
#   Create custom target for .py generator files.
#
macro(fips_handle_generators target) 
    if (CurProjectHasCodeGen)
        if (NOT TARGET ALL_GENERATE)
            add_custom_target(ALL_GENERATE
                COMMAND ${PYTHON} ${CMAKE_BINARY_DIR}/fips-gen.py ${CMAKE_BINARY_DIR}/fips_codegen.yml
                WORKING_DIRECTORY ${FIPS_PROJECT_DIR})
             if (CurTargetDependencies)
                add_dependencies(ALL_GENERATE ${CurTargetDependencies})
            endif()               
        endif()
        add_dependencies(${target} ALL_GENERATE)
    endif()
    if (CurTargetDependencies)
        add_dependencies(${target} ${CurTargetDependencies})
        unset(CurTargetDependencies)
    endif()
endmacro()

