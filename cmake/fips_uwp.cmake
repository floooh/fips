#-------------------------------------------------------------------------------
#   fips_uwp.cmake
#   Helper functions for building and deploying UWP apps.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#   fips_uwp_copy_default_assets
#   Copies the default logos/splashscreens etc to the UWP app's
#   build directory. These are then references in the app's package
#   manifest file.
#
macro(fips_uwp_copy_default_assets target)
    file(COPY "${FIPS_ROOT_DIR}/templates/uwp_assets" DESTINATION "${CMAKE_CURRENT_BINARY_DIR}")
    file(GLOB uwp_asset_files "${CMAKE_CURRENT_BINARY_DIR}/uwp_assets/*.png")
    list(APPEND CurSources ${uwp_asset_files})
    source_group("assets" FILES ${uwp_asset_files})
endmacro()

#-------------------------------------------------------------------------------
#   fips_uwp_generate_manifest
#   https://msdn.microsoft.com/en-us/library/windows/apps/br211475.aspx
#   FIXME: this just creates a placeholder manifest for debugging, need
#   to add proper support for user-provided manifest file (it should simply
#   check if an existing manifest file exists, and use that one)
#
macro(fips_uwp_generate_manifest target)
    set(FIPS_UWP_MANIFEST_PATH "${CMAKE_CURRENT_BINARY_DIR}/Package.appxmanifest")
    list(APPEND CurSources ${FIPS_UWP_MANIFEST_PATH})
    set(uwp_asset_root "uwp_assets")
    file(WRITE ${FIPS_UWP_MANIFEST_PATH}
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        "<Package\n"
        "  xmlns=\"http://schemas.microsoft.com/appx/manifest/foundation/windows10\"\n"
        "  xmlns:mp=\"http://schemas.microsoft.com/appx/2014/phone/manifest\"\n"
        "  xmlns:uap=\"http://schemas.microsoft.com/appx/manifest/uap/windows10\"\n"
        "  IgnorableNamespaces=\"uap mp\">\n"
        "  <Identity\n"
        "    Name=\"fips.uwp.app\"\n"
        "    Publisher=\"CN=Fips, O=Fips, L=FipsCity, S=FipsState, C=FipsCountry\"\n"
        "    Version=\"1.0.0.0\"/>\n"
        "  <mp:PhoneIdentity PhoneProductId=\"a2f5d340-13ff-434f-a136-d52a979c2073\" PhonePublisherId=\"00000000-0000-0000-0000-000000000000\"/>\n"
        "  <Properties>\n"
        "    <DisplayName>${target}</DisplayName>\n"
        "    <PublisherDisplayName>fips</PublisherDisplayName>\n"
        "    <Logo>${uwp_asset_root}\\StoreLogo.png</Logo>\n"
        "  </Properties>\n"
        "  <Dependencies>\n"
        "    <TargetDeviceFamily Name=\"Windows.Universal\" MinVersion=\"10.0.0.0\" MaxVersionTested=\"10.0.0.0\"/>\n"
        "  </Dependencies>\n"
        "  <Resources>\n"
        "    <Resource Language=\"x-generate\"/>\n"
        "  </Resources>\n"
        "  <Applications>\n"
        "    <Application Id=\"App\" Executable=\"$targetnametoken$.exe\" EntryPoint=\"${target}.App\">\n"
        "      <uap:VisualElements\n"
        "        DisplayName=\"${target}\"\n"
        "        Square150x150Logo=\"${uwp_asset_root}\\Square150x150Logo.png\"\n"
        "        Square44x44Logo=\"${uwp_asset_root}\\Square44x44Logo.png\"\n"
        "        Description=\"${target}\"\n"
        "        BackgroundColor=\"transparent\">\n"
        "        <uap:DefaultTile Wide310x150Logo=\"${uwp_asset_root}\\Wide310x150Logo.png\" />\n"
        "        <uap:SplashScreen Image=\"${uwp_asset_root}\\SplashScreen.png\" />\n"
        "      </uap:VisualElements>\n"
        "    </Application>\n"
        "  </Applications>\n"
        "  <Capabilities>\n"
        "    <Capability Name=\"internetClient\" />\n"
        "  </Capabilities>\n"
        "</Package>\n")
endmacro()

#-------------------------------------------------------------------------------
#   fips_uwp_add_target_properties(target)
#   Setup special target properties for UWP targets.
#
macro(fips_uwp_add_target_properties target)
    if (FIPS_UWP)
        fips_uwp_copy_default_assets(${target})
        fips_uwp_generate_manifest(${target})
    endif()
endmacro()
