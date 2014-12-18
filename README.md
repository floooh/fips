fips
====

**WORK IN PROGRESS**

- first progress video: https://www.youtube.com/watch?v=6F_AecDqRIY
- 2nd progress video: https://www.youtube.com/watch?v=W0MYjpR0G8c
- 3rd progress video: https://www.youtube.com/watch?v=3bQrYYaYU4w

**fips** is a combination of Python and cmake scripts to integrate existing build tools, IDEs and platform SDKs into an easy-to-use, high-level, multi-platform build system for C/C++ projects.

Or in other words: it's [Oryol's](https://github.com/floooh/oryol/blob/master/doc/BUILD.md) build system, moved into its own project, plus support for external dependencies.

Here's what **fips** can do for you:

- define a structure for C/C++ projects with external dependencies (_bundles_, _modules_, _libs_ and _apps_)
- create build files for make, ninja, Visual Studio, Xcode, QtCreator and more via cmake
- build on Linux, Windows and OSX with the platform-native compilers
- cross-compile to Android, iOS, emscripten and PNaCl
- automatically setup the Android, emscripten and PNaCl SDKs 
- manage the resulting dozens of different build configurations

[to be continued]
