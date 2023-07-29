#-------------------------------------------------------------------------------
#   fips_platform.cmake
#   Platform specific helper functions
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#   fips_vs_apply_options()
#   Applies the module-specific options set between begin/end, plus
#   any other MSVC specific target options.
#
#   FIXME: remove this
#
macro(fips_msvc_add_target_properties target)
    if (FIPS_MSVC)
        set_target_properties(${target} PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY ${FIPS_PROJECT_DEPLOY_DIR})
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_frameworks_osx(frameworks ...)
#   OSX specific: Add one or more OSX frameworks for linking with the
#   current target.
#
macro(fips_frameworks_osx frameworks)
    foreach (fw ${ARGV})
        target_link_libraries(${CurTargetName} "-framework ${fw}")
    endforeach()
endmacro()

#-------------------------------------------------------------------------------
#   fips_osx_generate_plist_file(target)
#
#   NOTE: the generated plist file can simply be overriden by adding
#   a .plist file to the target file list (this will then be stored in
#   FIPS_OSX_PLIST_PATH variable)
#
macro(fips_osx_generate_plist_file target)
    if (FIPS_IOS)
        if (NOT FIPS_OSX_PLIST_PATH)
            set(FIPS_OSX_PLIST_PATH ${CMAKE_CURRENT_BINARY_DIR}/Info.plist)
            file(WRITE ${FIPS_OSX_PLIST_PATH}
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
                "<plist version=\"1.0\">\n"
                "  <dict>\n"
                "    <key>CFBundleDevelopmentRegion</key>\n"
                "    <string>English</string>\n"
                "    <key>CFBundleDisplayName</key>\n"
                "    <string>\${MACOSX_BUNDLE_BUNDLE_NAME}</string>\n"
                "    <key>CFBundleExecutable</key>\n"
                "    <string>\${MACOSX_BUNDLE_EXECUTABLE_NAME}</string>\n"
                "    <key>CFBundleIconFile</key>\n"
                "    <string>\${MACOSX_BUNDLE_ICON_FILE}</string>\n"
                "    <key>CFBundleIconFiles</key>\n"
                "    <array>\n"
                "      <string>icon.png</string>\n"
                "      <string>icon-57.png</string>\n"
                "      <string>icon-114.png</string>\n"
                "    </array>\n"
                "    <key>CFBundleIdentifier</key>\n"
                "    <string>\${MACOSX_BUNDLE_GUI_IDENTIFIER}</string>\n"
                "    <key>CFBundleInfoDictionaryVersion</key>\n"
                "    <string>6.0</string>\n"
                "    <key>CFBundleName</key>\n"
                "    <string>\${MACOSX_BUNDLE_BUNDLE_NAME}</string>\n"
                "    <key>CFBundlePackageType</key>\n"
                "    <string>APPL</string>\n"
                "    <key>CFBundleSignature</key>\n"
                "    <string>????</string>\n"
                "    <key>CFBundleVersion</key>\n"
                "    <string>1.0.0</string>\n"
                "    <key>CFBundleShortVersionString</key>\n"
                "    <string>1.0.0</string>\n"
                "    <key>LSRequiresIPhoneOS</key>\n"
                "    <true/>\n"
                "    <key>UIStatusBarHidden</key>\n"
                "    <true/>\n"
                "    <key>UIViewControllerBasedStatusBarAppearance</key>\n"
                "    <false/>\n"
                "    <key>UIInterfaceOrientation</key>\n"
                "    <string>UIInterfaceOrientationLandscapeRight</string>\n"
                "    <key>UISupportedInterfaceOrientations</key>\n"
                "    <array>\n"
                "      <string>UIInterfaceOrientationLandscapeRight</string>\n"
                "    </array>\n"
                "    <key>UIRequiredDeviceCapabilities</key>\n"
                "    <array>\n"
                "      <string>opengles-2</string>\n"
                "      <string>armv7</string>\n"
                "      <string>accelerometer</string>\n"
                "    </array>\n"
                "    <key>NSAppTransportSecurity</key>\n"
                "    <dict>\n"
                "      <key>NSAllowsArbitraryLoads</key>\n"
                "      <true/>\n"
                "    </dict>\n"
                "  </dict>\n"
                "</plist>\n")
        endif()
    elseif (FIPS_MACOS)
        if (NOT FIPS_OSX_PLIST_PATH)
            set(FIPS_OSX_PLIST_PATH ${CMAKE_CURRENT_BINARY_DIR}/Info.plist)
            file(WRITE ${FIPS_OSX_PLIST_PATH}
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
                "<plist version=\"1.0\">\n"
                "  <dict>\n"
                "    <key>CFBundleDevelopmentRegion</key>\n"
                "    <string>English</string>\n"
                "    <key>CFBundleDisplayName</key>\n"
                "    <string>\${MACOSX_BUNDLE_BUNDLE_NAME}</string>\n"
                "    <key>CFBundleExecutable</key>\n"
                "    <string>\${MACOSX_BUNDLE_EXECUTABLE_NAME}</string>\n"
                "    <key>CFBundleIconFile</key>\n"
                "    <string>\${MACOSX_BUNDLE_ICON_FILE}</string>\n"
                "    <key>CFBundleIconFiles</key>\n"
                "    <array>\n"
                "      <string>icon.png</string>\n"
                "      <string>icon-57.png</string>\n"
                "      <string>icon-114.png</string>\n"
                "    </array>\n"
                "    <key>CFBundleIdentifier</key>\n"
                "    <string>\${MACOSX_BUNDLE_GUI_IDENTIFIER}</string>\n"
                "    <key>CFBundleInfoDictionaryVersion</key>\n"
                "    <string>6.0</string>\n"
                "    <key>CFBundleName</key>\n"
                "    <string>\${MACOSX_BUNDLE_BUNDLE_NAME}</string>\n"
                "    <key>CFBundlePackageType</key>\n"
                "    <string>APPL</string>\n"
                "    <key>CFBundleShortVersionString</key>\n"
                "    <string>1.0</string>\n"
                "    <key>CFBundleSignature</key>\n"
                "    <string>????</string>\n"
                "    <key>CFBundleVersion</key>\n"
                "    <string>1</string>\n"
                "    <key>LSMinimumSystemVersion</key>\n"
                # NOT A BUG:
                "    <string>\$(MACOSX_DEPLOYMENT_TARGET)</string>\n"
                "    <key>NSHighResolutionCapable</key>\n"
                "    <true/>\n"
                "    <key>NSAppTransportSecurity</key>\n"
                "    <dict>\n"
                "      <key>NSAllowsArbitraryLoads</key>\n"
                "      <true/>\n"
                "    </dict>\n"
                "  </dict>\n"
                "</plist>\n")
        endif()
    endif()
    set_target_properties(${target} PROPERTIES MACOSX_BUNDLE_INFO_PLIST ${FIPS_OSX_PLIST_PATH})
endmacro()

#-------------------------------------------------------------------------------
#   fips_osx_add_target_properties(target)
#   Setup special target properties for OSX/iOS.
#
macro(fips_osx_add_target_properties target)
    if (FIPS_OSX)
        fips_osx_generate_plist_file(${target})
        if (FIPS_IOS)
            set_target_properties(${target} PROPERTIES XCODE_ATTRIBUTE_CODE_SIGN_IDENTITY "iPhone Developer")
            set_target_properties(${target} PROPERTIES XCODE_ATTRIBUTE_TARGETED_DEVICE_FAMILY "1,2")
            if (FIPS_IOS_TEAMID)
                set_target_properties(${target} PROPERTIES XCODE_ATTRIBUTE_DEVELOPMENT_TEAM ${FIPS_IOS_TEAMID})
            endif()
        endif()
        set_target_properties(${target} PROPERTIES MACOSX_BUNDLE_ICON_FILE "Icon.png")
        if (FIPS_MACOS)
            set_target_properties(${target} PROPERTIES XCODE_SCHEME_WORKING_DIRECTORY "${FIPS_PROJECT_DEPLOY_DIR}")
        endif()
        if (${CMAKE_GENERATOR} STREQUAL "Xcode")
            set_target_properties(${target} PROPERTIES XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER \${PRODUCT_NAME})
            set_target_properties(${target} PROPERTIES MACOSX_BUNDLE_GUI_IDENTIFIER \${PRODUCT_NAME})
            set_target_properties(${target} PROPERTIES MACOSX_BUNDLE_EXECUTABLE_NAME \${EXECUTABLE_NAME})
            set_target_properties(${target} PROPERTIES MACOSX_BUNDLE_PRODUCT_NAME \${PRODUCT_NAME})
            set_target_properties(${target} PROPERTIES MACOSX_BUNDLE_BUNDLE_NAME \${PRODUCT_NAME})
        else()
            set_target_properties(${target} PROPERTIES XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER "${target}")
            set_target_properties(${target} PROPERTIES MACOSX_BUNDLE_GUI_IDENTIFIER "${target}")
            set_target_properties(${target} PROPERTIES MACOSX_BUNDLE_PRODUCT_NAME "${target}")
            set_target_properties(${target} PROPERTIES MACOSX_BUNDLE_BUNDLE_NAME "${target}")
        endif()
    endif()
endmacro()

#-------------------------------------------------------------------------------
#   fips_android_postbuildstep
#
macro(fips_android_postbuildstep target)
    if (FIPS_ANDROID)
        add_custom_command(TARGET ${target} POST_BUILD
            COMMAND ${PYTHON} ${FIPS_ROOT_DIR}/tools/android-create-apk.py
            --path ${CMAKE_CURRENT_BINARY_DIR}
            --name ${target}
            --abi ${CMAKE_ANDROID_ARCH_ABI}
            --version ${ANDROID_PLATFORM_LEVEL}
            --package org.fips.${target}
            --deploy ${FIPS_DEPLOY_DIR}/${FIPS_PROJECT_NAME}/${FIPS_CONFIG})
    endif()
endmacro()
