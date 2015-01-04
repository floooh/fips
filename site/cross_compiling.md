---
layout: page
title: Cross-Compiling
permalink: /crosscompile/
---

### Cross-Compiling

Fips provides easy cross-compiling support to the following platforms:

- iOS
- Android (https://developer.android.com/tools/sdk/ndk/index.html)
- emscripten (http://kripken.github.io/emscripten-site/index.html)
- PNaCl (https://developer.chrome.com/native-client)

Cross-compilation to iOS is only supported on the OSX host platform. All
other target platforms are supported on all 3 host platforms (OSX, Linux, Windows).


#### Setting up the platform SDKs

Fips provides simple commands to setup the SDKs for Android, emscripten and
PNaCl:

```bash
> ./fips setup emscripten
> ./fips setup nacl
> ./fips setup android
```

This will download, unpack and setup the respective SDKs into a directory
_fips-sdks_ next to the fips directory.

> NOTE: there is currently no way to use an SDK installed to another location

You should also run 'fips diag tools' to make sure that all required
tools are in the path:

```bash
> ./fips diag tools

```

#### Testing cross-compilation

Cross-compilation requires a portable code base, in the case of Android and
PNaCl this is a bit non-trivial (e.g. the canonical C 'Hello World' doesn't
work). Let's use the Oryol 3D engine for testing:

```bash
> ./fips clone oryol
> cd ../oryol
```

First let's try whether **emscripten** compilation works:

```bash
> ./fips set config emsc-make-release
> ./fips build
...
> ./fips run Triangle
```

The last command should open the default web browser and a local http server.
It may be necessary to refresh the page in case the http server needs too long
to start.

Cross-compiling to **PNaCl** is just as easy, just use a different config:

```bash
> ./fips set config pnacl-make-release
> ./fips build
...
> ./fips run Triangle
```

Same for **Android**, note that Android provides 3 types of config, one for each
CPU type. 'Running' an Android will only deploy the application to the device,
after that it must be started manually.

> NOTE: './fips run' for Android is not implemented yet

```bash
> ./fips build android-make-release
> ./fips build androidx86-make-release
> ./fips build androidmips-make-release

> NOTE: Android MIPS is not yet fully supported on Oryol!
```

Finally iOS: this works a bit diffently since iOS compiling and debugging
works best directly in Xcode. Instead of a command line build, we only 
generate the Xcode project files, and then start Xcode:

```bash
> ./fips set config ios-xcode-debug
> ./fips gen
> ./fips open
```

Once in Xcode, the samples can be compiled and debugged either in the simulator
or on a real device (provided Xcode is properly setup for iOS development).

#### Under the hood

Cross-compiling currently has a few caveats:

* it is currently not possible to use existing SDKs in other filesystem locations
* the _emscripten_ SDK always uses the _incoming_ branch, not the _master_ branch
* the NaCl SDK currently always uses the pepper_canary API version
* for Android, 'universal binaries' containing ARM, X86 and MIPS binaries are 
  currently not supported

Cross-compiling build settings are defined in cmake toolchain files in:

* fips/cmake-toolchains/android.toolchain.cmake
* fips/cmake-toolchains/emscripten.toolchain.cmake
* fips/cmake-toolchains/ios.toolchain.cmake
* fips/cmake-toolchains/pnacl.toolchain.cmake

For some target platforms, cmake generates additional files during the cmake run:

On **Android**, a Java wrapper application directory and AndroidManifest.xml 
file is created (see fips/cmake/fips_android.cmake).

On **PNaCl**, a manifest (.nmf) and a HTML file is generated, and the PNaCl 
finalizer tool is run as post-build-step (see fips/cmake/fips_pnacl.cmake).

On **iOS**, a .plist file is generated (see fips/cmake/fips_osx.cmake).

