#-------------------------------------------------------------------------------
#   android.py
#
#   Helper script to create an APK project directory and create
#   an APK.
#
#   The Android SDK is expected under "fips-sdks/android/"
#
#   Arguments:
#
#   --path [path-to-cmake-build-dir]
#   --name [target-name]
#   --abi ["armeabi-v7a"|"mips"|"x86"]
#   --platform ["android-21"]
#   --package [package-name]
#
#   Result will be a name.apk file in 'path'.
#
import sys
import os
import argparse
import shutil

parser = argparse.ArgumentParser(description="Android APK package helper.")
parser.add_argument('--sdk', help='path to Android SDK', required=True)
parser.add_argument('--path', help='path to the cmake build dir', required=True)
parser.add_argument('--name', help='cmake target name', required=True)
parser.add_argument('--abi', help='the NDK ABI string (armeabi-v7a, mips or x86', default='armeabi-v7a')
parser.add_argument('--version', help='the Android SDK platform version (e.g. 21)', default='21')
parser.add_argument('--package', help='the Java package name', required=True)
args = parser.parse_args()

# create the empty project
apk_dir = args.path + '/android/'
if not os.path.exists(apk_dir):
    os.makedirs(apk_dir)
libs_dir = apk_dir + 'libs/' + args.abi + '/'
if not os.path.exists(libs_dir):
    os.makedirs(libs_dir)
res_dir = apk_dir + 'res/drawable/'
if not os.path.exists(libs_dir):
    os.makedirs(res_dir)
src_dir = (apk_dir + 'src/' + args.package).replace('.', '/')
if not os.path.exists(src_dir):
    os.makedirs(src_dir)

# copy the native shared library
so_name = 'lib' + args.name + '.so'
src_so = args.path + so_name
dst_so = libs_dir + so_name
print src_so, dst_so
shutil.copy(src_so, dst_so)

# generate AndroidManifest.xml
with open(apk_dir + 'AndroidManifest.xml', 'w') as f:
    f.write('<manifest xmlns:android="http://schemas.android.com/apk/res/android"\n')
    f.write('  package="{}"\n'.format(args.package))
    f.write('  android:versionCode="1"\n')
    f.write('  android:versionName="1.0">\n')
    f.write('  <uses-sdk android:minSdkVersion="11" android:targetSdkVersion="{}"/>\n'.format(args.version))
    f.write('  <uses-permission android:name="android.permission.INTERNET"></uses-permission>\n')
    f.write('  <uses-feature android:glEsVersion="0x00030000"></uses-feature>\n')
    f.write('  <application android:label="{}" android:hasCode="false">\n'.format(args.name))
    f.write('    <activity android:name="android.app.NativeActivity"\n');
    f.write('      android:label="{}"\n'.format(args.name))
    f.write('      android:theme="@android:style/Theme.NoTitleBar.Fullscreen"\n')
    f.write('      android:launchMode="singleTask"\n')
    f.write('      android:screenOrientation="landscape"\n')
    f.write('      android:configChanges="orientation|keyboardHidden">\n')
    f.write('      <meta-data android:name="android.app.lib_name" android:value="{}"/>\n'.format(args.name))
    f.write('      <intent-filter>\n')
    f.write('        <action android:name="android.intent.action.MAIN"/>\n')
    f.write('        <category android:name="android.intent.category.LAUNCHER"/>\n')
    f.write('      </intent-filter>\n')
    f.write('    </activity>\n')
    f.write('  </application>\n')
    f.write('</manifest>\n')
