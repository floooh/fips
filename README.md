fips
====

**WORK IN PROGRESS**

**fips** is mainly a **cmake build configuration juggler** for 
multi-platform C/C++ projects. Complex projects often have dozens of different
build configurations for combinations of host- and target-platforms, 
different build types (e.g. Release, Debug, Profiling), need different builds for
deployment or testing, need to integrate external code and so on. **fips** 
manages all these different build configurations, keeps them all nicely 
separated from each other, and allows to process build configurations
in batches.

But build configuration management is just the 'tip of the iceberg', it
also provides other features to simplify setting up and working with
complex multi-platform C/C++ projects:

### Features

* manage many separate cmake build configurations
* import external code modules from git repos
* project structure is described with a simplified cmake syntax
* multi-platform-support using the platform-native build tools:
    * Linux: make, ninja, gcc, clang, cmake-compatible IDEs
    * OSX: Xcode, make, ninja, gcc, clang
    * Windows: Visual Studio
* easy cross-compiling-support to:
    * Android (Android NDK)
    * iOS
    * emscripten
    * Portable Native Client (PNaCl)
* compile-time code generation via python scripts
* extensible via python plugin modules

### What fips is **not**

* fips isn't a game asset exporter pipeline
* fips isn't a distributed build system (like Incredibuild)
* fips isn't a general build job scheduler (like Jenkins)
* fips isn't a replacement for cmake, premake, scons etc...

### Documentation

* [Getting Started](doc/getting_started.md)

### Progress

fips is currently heavily **work in progress**, everything may change or
break at any time.

I'm trying to put up progress videos from time to time:

- first progress video: https://www.youtube.com/watch?v=6F_AecDqRIY
- 2nd progress video: https://www.youtube.com/watch?v=W0MYjpR0G8c
- 3rd progress video: https://www.youtube.com/watch?v=3bQrYYaYU4w
- 4th progress video: https://vimeo.com/115050871
- using fips with Oryol 3D engine: https://www.youtube.com/watch?v=LaC4Sqatyts
- compiling and debugging in QtCreator and CLion IDEs: https://www.youtube.com/watch?v=Sp5TywYeNzE
- building a standalone Oryol app: https://www.youtube.com/watch?v=z8nwrGh2Zsc

