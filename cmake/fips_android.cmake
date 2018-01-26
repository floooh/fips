#-------------------------------------------------------------------------------
#   fips_android.cmake
#   Helper functions for building and deploying Android apps.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#   fips_android_create_project(target)
#   Create Android project wrapper for a given target.
#
macro(fips_android_create_project target)
    
    # call python helper script to setup the Android project directory which
    # will be converted to an APK in the post build step
    add_custom_command(TARGET ${target} POST_BUILD 
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMAND ${PYTHON} ${FIPS_ROOT_DIR}/tools/android.py 
            --create ${SMAKE_CURRENT_BINARY_DIR}/android
            --api ${ANDROID_API}
            --name ${target}
    )

    # call the android SDK tool to create a new project (skip if already exists)
    if (NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/android)
        message("=> create Android SDK project: ${target}")
        execute_process(COMMAND ${ANDROID_SDK_TOOL} --silent create project
                        --path ${CMAKE_CURRENT_BINARY_DIR}/android
                        --target ${ANDROID_API}
                        --name ${target}
                        --package com.fips.${target}
                        --activity DummyActivity
                        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
    endif()

    # set the output directory for the .so files to point to the android project's 'lib/[cpuarch] directory
    set(ANDROID_SO_OUTDIR ${CMAKE_CURRENT_BINARY_DIR}/android/libs/${ANDROID_NDK_ARCH})
    set_target_properties(${target} PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${ANDROID_SO_OUTDIR})
    set_target_properties(${target} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_RELEASE ${ANDROID_SO_OUTDIR})
    set_target_properties(${target} PROPERTIES LIBRARY_OUTPUT_DIRECTORY_DEBUG ${ANDROID_SO_OUTDIR})

    # override AndroidManifest.xml 
    file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/android/AndroidManifest.xml
        "<manifest xmlns:android=\"http://schemas.android.com/apk/res/android\"\n"
        "  package=\"com.fips.${target}\"\n"
        "  android:versionCode=\"1\"\n"
        "  android:versionName=\"1.0\">\n"
        "  <uses-sdk android:minSdkVersion=\"11\" android:targetSdkVersion=\"19\"/>\n"
        "  <uses-permission android:name=\"android.permission.INTERNET\"></uses-permission>\n"
        "  <uses-feature android:glEsVersion=\"0x00030000\"></uses-feature>\n"
        "  <application android:label=\"Oryol ${target}\" android:hasCode=\"false\">\n"
        "    <activity android:name=\"android.app.NativeActivity\"\n"
        "      android:label=\"Oryol ${target}\"\n"
        "      android:theme=\"@android:style/Theme.NoTitleBar.Fullscreen\"\n"
        "      android:launchMode=\"singleTask\"\n"
        "      android:screenOrientation=\"landscape\"\n"
        "      android:configChanges=\"orientation|keyboardHidden\">\n"
        "      <meta-data android:name=\"android.app.lib_name\" android:value=\"${target}\"/>\n"
        "      <intent-filter>\n"
        "        <action android:name=\"android.intent.action.MAIN\"/>\n"
        "        <category android:name=\"android.intent.category.LAUNCHER\"/>\n"
        "      </intent-filter>\n"
        "    </activity>\n"
        "  </application>\n"
        "</manifest>\n")

endmacro()

#-------------------------------------------------------------------------------
#   fips_android_postbuildstep
#
macro(fips_android_postbuildstep target)
    if ("${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
        set(ANT_BUILD_TYPE "debug")
    else()
        # NOTE: not a bug, just allow debug-signed apps with native optimizations
        set(ANT_BUILD_TYPE "debug")
    endif()
    add_custom_command(TARGET ${target} POST_BUILD COMMAND ${ANDROID_ANT} ${ANT_BUILD_TYPE} WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/android)
    add_custom_command(TARGET ${target} POST_BUILD COMMAND ${CMAKE_COMMAND} -E make_directory ${FIPS_DEPLOY_DIR}/${FIPS_PROJECT_NAME}/${FIPS_CONFIG} COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_BINARY_DIR}/android/bin/${target}-debug.apk ${FIPS_DEPLOY_DIR}/${FIPS_PROJECT_NAME}/${FIPS_CONFIG}/)
endmacro()

