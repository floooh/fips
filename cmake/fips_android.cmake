#-------------------------------------------------------------------------------
#   fips_android.cmake
#   Helper functions for building and deploying Android apps.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#   fips_android_postbuildstep
#
macro(fips_android_postbuildstep target)
    add_custom_command(TARGET ${target} POST_BUILD
        COMMAND python ${FIPS_ROOT_DIR}/tools/android-create-apk.py
        --path ${CMAKE_CURRENT_BINARY_DIR}
        --name ${target}
        --abi ${CMAKE_ANDROID_ARCH_ABI}
        --package org.fips.${target}
        --deploy ${FIPS_DEPLOY_DIR}/${FIPS_PROJECT_NAME}/${FIPS_CONFIG})
endmacro()

