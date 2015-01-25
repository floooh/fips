#-------------------------------------------------------------------------------
#   fips_generators.cmake
#   Helper cmake functions for integrating python generator scripts into 
#   the build process.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#   fips_handle_py_files_pretarget(pyFiles)
#   Adds a .cc and .h file for each .py generator file.
#
macro(fips_handle_py_files_pretarget pyFiles)
    foreach(pyFile ${pyFiles})
        string(REPLACE .py .cc src ${pyFile})
        string(REPLACE .py .h hdr ${pyFile})
        if (NOT EXISTS ${src})
            file(WRITE ${src} " ")
        endif()
        if (NOT EXISTS ${hdr})
            file(WRITE ${hdr} " ")
        endif()
    endforeach()    
endmacro()

#-------------------------------------------------------------------------------
#   fips_handle_py_files_posttarget(target pyFiles)
#   Create custom target for .py generator files.
#
macro(fips_handle_py_files_posttarget target pyFiles)
    if (PYTHON)
        # ...and add a custom target to build the sources
        add_custom_target(${target}_py 
            COMMAND ${PYTHON} ${FIPS_PROJECT_DIR}/.fips-gen.py ${pyFiles} 
            WORKING_DIRECTORY ${FIPS_PROJECT_DIR}
            COMMENT "Generating sources from ${pyFiles}...")
        set_target_properties(${target}_py PROPERTIES FOLDER "Generators")
        add_dependencies(${target} ${target}_py)
    else()  
        message("WARNING: Python not found, skipping python generators!")
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_handle_gen_items_pretarget(target genItems)
#   Handle generic code generation items, each item is of the form
#   'generator#file' where generator is a Python generator script under
#   project-dir/fips-generators, and file is an input file for that 
#   generator. This macro will create one .cc and one .h file per item
#
macro(fips_handle_items_pretarget target genItems)
    foreach(item ${genItems})
        STRING(REPLACE "#" ";" tokens ${item})
        list(GET ${tokens} 0 generator)
        list(GET ${tokens} 0 filename)
        get_filename_component(fext ${filename} EXT)

        # replace file extension with .cc / .h
        string(REPLACE ${fext} .cc src ${filename})
        string(REPLACE ${fext} .h hdr ${filename})
        if (NOT EXISTS ${src})
            file(WRITE ${src} " ")
        endif()
        if (NOT EXISTS ${hdr})
            file(WRITE ${hdr} " ")
        endif()
    endforeach()
endmacro()

#-------------------------------------------------------------------------------
#   fips_handle_gen_items_posttarget(target genItems)
#   Create custom target for generic code generation items.
#
macro(fips_handle_gen_items_posttarget target genItems)
    if (PYTHON)
        add_custom_target(${target}_gen
            COMMAND ${PYTHON} ${FIPS_PROJECT_DIR}/.fips-gen.py ${genItems}
            WORKING_DIRECTORY ${FIPS_PROJECT_DIR}
            COMMENT "Generating source from ${genItems}...")
        set_target_properties(${target}_gen PROPERTIES FOLDER "Generators")
        add_dependencies(${target} ${target}_gen)
    else()
        message("WARNING: Python not found, skipping code generation!")
    endif()
endmacro()


