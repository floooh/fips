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
#       python script (located under project-dir/fips-generators),
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
#   fips_add_python_generator(py_file)
#   Add a code-generator python file to the current target. This is one of
#   two ways for code generation, just list a python file as normal 
#   source which will be executed and creates a .cc and .h file.
#   
macro(fips_add_python_generator group_name py_file)
    if (FipsAddFilesEnabled)
        get_filename_component(f_abs ${py_file} ABSOLUTE)
        get_filename_component(f_dir ${f_abs} DIRECTORY)
        get_filename_component(f_name ${f_abs} NAME_WE)
        set(gen_src "${f_dir}/${f_name}.cc")
        set(gen_hdr "${f_dir}/${f_name}.h")
        file(APPEND "${CMAKE_BINARY_DIR}/fips_codegen.yml" 
            "- type: simple\n"
            "  script: '${f_abs}'\n"
            "  outputs:\n"
            "    - '${gen_src}'\n"
            "    - '${gen_hdr}'\n")
        list(APPEND CurSources ${gen_src} ${gen_hdr})
        source_group("${group_name}\\gen" FILES ${gen_src} ${gen_hdr})
        if (NOT EXISTS ${gen_src})
            file(WRITE ${gen_src} " ")
        endif()
        if (NOT EXISTS ${gen_hdr})
            file(WRITE ${gen_hdr} " ")
        endif()
        set(CurProjectHasCodeGen 1)
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_add_file_generator(in_file generator out_files)
#   Add a code generator item (in_file -> generator -> out_files) to the
#   current target.
#
macro(fips_add_file_generator group_name in_file generator out_files)
    if (FipsAddFilesEnabled)
        get_filename_component(f_abs ${in_file} ABSOLUTE)
        get_filename_component(f_dir ${f_abs} DIRECTORY)
        set(yml_content 
            "- type: generic\n"
            "  generator: ${generator}\n"
            "  input: '${f_abs}'\n"
            "  outputs:\n")
        foreach(out_file ${out_files})
            set(out_path "${f_dir}/${out_file}")
            string(CONCAT yml_content ${yml_content} "  - '${out_path}'")
            list(APPEND CurSources ${out_path})
            source_group("${group_name}\\gen" FILES ${out_path})
            if (NOT EXISTS ${out_path})
                file(WRITE ${out_path} " ")
            endif()
        endforeach()
        file(APPEND "${CMAKE_BINARY_DIR}/fips_codegen.yml" "${yml_content}")
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
                COMMAND ${PYTHON} ${FIPS_PROJECT_DIR}/.fips-gen.py ${CMAKE_BINARY_DIR}/fips_codegen.yml
                WORKING_DIRECTORY ${FIPS_PROJECT_DIR}
                COMMENT "Generating code...")
        endif()
        add_dependencies(${target} ALL_GENERATE)
    endif()
endmacro()

