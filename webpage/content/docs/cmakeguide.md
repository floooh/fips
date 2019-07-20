---
title: "CMake Guide"
weight: 5
# bookFlatSection: false
# bookShowToC: true
---
# Fips CMake Guide

Fips projects need to adhere to a few rules in their CMakeLists.txt file
hierarchy. Fips provides a number of cmake macros, variables and toolchain
files to simplify working with cmake files and implement some under-the-hood
magic.

### Fips CMake Macros

Fips provides the following cmake macros to describe a project structure:

#### fips\_setup()

Initializes the fips build system in a cmake file hierarchy. Must be
called once in the root CMakeLists.txt before any other fips cmake
macros.

You *must* call the cmake command 'project([proj\_name])' before fips\_setup()
to define a project name. Starting with version 3.15, cmake will issue
a warning if the toplevel CMakeLists.txt file doesn't contain a verbatim
project() statement.

#### fips\_finish()

Must be called in the root CMakeLists.txt file after any other fips macros
and does any work that must happen once after each cmake run. Currently
this is macro does nothing.

#### fips\_project(name)

Starts a new project with the given name. This must be called at least
once in a hierarchy of CMakeLists.txt files, usually right after 
fips\_setup(). 

Use the fips\_project() macro instead of cmake's builtin project() macro

#### fips\_ide\_group(name)

Start a new project explorer folder in an IDE. This can be used to 
group related build targets for a clearer layout in the IDE's project 
explorer.

#### fips\_add\_subdirectory(dir)

Include a child CMakeLists.txt file from a subdirectory. Use this instead
of cmake's built-in add\_subdirectory() macro.

#### fips\_include\_directories(dir ...)

Define one or more header search paths. Use this instead of
cmake's built-in include\_directories() macro.

#### fips\_begin\_module(name)

Begin defining a fips module. Modules are special high-level static link-libraries
with a few additional features over conventional libs:

* can define dependencies to other modules, which are automatically
  resolved when linking apps
* can contain code-generation python scripts which are added as 
  custom build targets to the build process

After a fips\_begin\_module() the following fips macros are valid:

* fips\_dir()
* fips\_files()
* fips\_generate()
* fips\_deps()
* fips\_libs()
* fips\_end\_module()

#### fips\_end\_module()

This finishes a fips\_begin\_module() block.

#### fips\_begin\_lib(name)

Begin defining a fips library. A fips library is a collection of source
files that compile into a static link library. Fips libraries are normally 
used to wrap 3rd-party code that would normally be linked as a pre-compiled
static link library, but is instead compiled from source code into
a fips project.

> NOTE: currently, a fips library is equivalent to a fips module, this
may change in the future though

After a fips\_begin\_lib() the following fips macros are valid:

* fips\_dir()
* fips\_files()
* fips\_generate()
* fips\_deps()
* fips\_libs()
* fips\_end\_lib()

#### fips\_end\_lib()

This finishes a fips\_begin\_lib() block.

#### fips\_begin\_sharedlib(name)

Begin defining a fips shared library. A fips shared library is a collection of source
files that compile into a dynamically linkable library (as opposed to static libraries).

After a fips\_begin\_sharedlib() the following fips macros are valid:

* fips\_dir()
* fips\_files()
* fips\_generate()
* fips\_deps()
* fips\_libs()
* fips\_end\_sharedlib()

#### fips\_end\_sharedlib()

This finishes a fips\_begin\_sharedlib() block.

#### fips\_begin\_app(name type)

Begin defining a fips application. The _type_ argument can be either 'windowed'
or 'cmdline', this only makes a difference on platform with separate
command-line and UI application types, like Windows (WinMain vs main)
or OSX (app bundle vs command line tool).

The executable target (and only the executable target) will see the following 
preprocessor definitions:

```c
// fips_begin_app(bla windowed)
#define FIPS_APP_WINDOWED (1)
// fips_begin_app(bla cmdline)
#define FIPS_APP_CMDLINE (1)
```

On Windows this can be used to select between main() or WinMain() 
as app entry function.

After a fips\_begin\_app() the following fips macros are valid:

* fips\_dir()
* fips\_files()
* fips\_generate()
* fips\_deps()
* fips\_libs()
* fips\_end\_app()

#### fips\_end\_app()

This finishes a fips\_begin\_app() block.

#### fips\_dir(dir [GROUP ide\_group])

Defines a source code subdirectory for the following fips\_files() statements.
This is only necessary if source files are located in subdirectories of the
directory where the current CMakeLists.txt file is located. You don't need
to provide a fips\_dir() statement for files in the same directory as 
their CMakeLists.txt file.

fips will automatically derive an IDE group folder name from the directory
path, so that the directory structure is reflected in IDE file explorers.
This behaviour can be overriden with the optional GROUP argument, and 
an explicit group name (or path) can be defined.

This is the default usage of fips\_dir, without explicitly overriding
the IDE group name:

```cmake
fips_dir(android)
```

This would switch the 'current source directory' to a subdirectory named
'android', and in IDEs these files will be grouped under a folder 'android'
in the file explorer.

To switch back to the root directory (where the CMakeLists.txt file is located),
just pass a . as argument:

```cmake
fips_dir(.)
```

The following example groups files in a very deep directory hierarchy
under a short group name "include":

```cmake
fips_dir(some/deep/dir/hierarchy/include GROUP "include")
```

A GROUP argument can also contain slashes to define a whole group path:

```cmake
fips_dir(some/deep/dir/hierarchy/include GROUP "engine/include")
```

Finally, to not put the files into any IDE group folder, pass a 
"." as special GROUP argument:

```cmake
fips_dir(some/deep/dir/hierarchy/include GROUP ".")
```

fips\_dir() must be called inside a module, lib, or app definition block.

#### fips\_files(file ...)

Add source files in the currently set directory to the current module, lib or app.
This isn't restricted to C/C++ files, but any file that should show
up in the IDE project explorer. The actual build process will ignore any
files with file extensions that cmake doesn't know how to build.

The following file extensions are recognized by the build process:

* **.cc, .cpp**:    C++ source files (compiled with C++11 support)
* **.c**:           C source files
* **.m, .mm**:      Objective-C and Objective-C++ source files
* **.h, .hh**:      C/C++/Obj-C headers
* **.py**:          Python source code generator scripts
* **.plist**:       on iOS and MacOS, a file with the extension **.plist** overrides the default Info.plist file generated by fips

fips\_files() must be called inside a module, lib, or app definition block.

#### fips\_files\_ex(dir glob... \[EXCEPT glob...\] \[GROUP ide\_group\] \[NO\_RECURSE|GROUP\_FOLDERS\])

Like fips\_dir(), but will also do a fips\_files() with files found in a directory
that match an expression from the glob expression list excluding any file that
is in the ```EXCEPT``` glob expression list. You can use ```NO_RECURSE``` so it will not
search files in subdirectories. The flag ```GROUP_FOLDERS``` will enable the automatic creation of groups that reflect folders in the filesystem.

To add all files contained in a folder but excluding some types to the group 
"everything":

```cmake
fips_files_ex(src/ *.* EXCEPT *.rc *.txt GROUP "everything")
```

Or, if you do want only Objective-C sources for example:

```cmake
fips_files_ex(src/ *.m *.mm GROUP "ObjC")
```

Note: You should avoid using this as CMake will not be able to detect when files
are added or removed to the filesystem and consequently will not be able to 
reconfigure the project. A good use of this is if it can help porting libraries 
to fips.

fips\_files\_ex() must be called inside a module, lib, or app definition block.

#### fips\_src(dir glob... \[EXCEPT glob...\] \[GROUP ide\_group\] \[NO\_RECURSE|GROUP\_FOLDERS\])

Same as fips\_files\_ex() but with a default list of expressions valid for C/C++
projects: *.c *.cc *.cpp *.h *.hh *.hpp

So you can easily add any C/C++ sources from the directory "src/" to the project
as simply as:

```cmake
fips_src(src)
```

fips\_src() must be called inside a module, lib, or app definition block.

#### fips\_deps(dep ...)

Add module or lib dependencies to the current fips app, module or lib. A
dependency must be the name of another fips module or lib defined
with fips\_begin\_module() or fips\_begin\_lib(). Dependencies added to 
fips modules will be resolved recursively
when linking apps. Fips will also take care of the dreaded linking order
problem of GCC where symbols can't be resolved if the
order of link libraries is wrong or in case of cyclic dependencies.

fips\_deps() must be called inside a module, lib, or app definition block.

> NOTE: dependencies listed in fips\_deps() must have been defined before
> in the CMakeLists.txt file hierarchy

#### fips\_libs(libs ...)

Add a static link library dependency to the current fips app, module or libs.
This is similar to the fips\_deps() macro but is used to define a link
dependency to an existing, precompiled static link library. 

fips\_libs() must be called inside a module, lib, or app definition block.

#### fips\_libs\_debug(libs ...), fips\_libs\_release(libs ...)

These are rarely needed special variants of **fips\_libs()** which add separate 
static link libraries for debug and non-debug compilation modes. This is necessary
on Visual Studio when trying to link libraries that contain STL code.

#### fips\_generate(...)

Defines a code-generation job. Code generation can be used to generate
C/C++ source files at build time from other input files like JSON,
XML, YAML, GLSL, ... Code generation is described in detail 
[here](codegen.html)

fips\_generate() must be called inside a module, lib, or app definition block.

### The fips-include.cmake File

A fips project may contain an optional cmake file called **fips-include.cmake**
at the root level of a project (same directory level as the root
CMakeLists.txt file). The fips-include.cmake file should contain all cmake
definitions that need to be visible when using this fips project as an
external dependency in another project. Fips will include this file either
when the project itself is compiled, or the project is imported as an
external dependency in other projects.

Check out the [fips-include.cmake](https://github.com/floooh/oryol/blob/master/fips-files/include.cmake)
file included in the Oryol 3D engine for a complex example.

### Fips Predefined CMake Variables

Fips defines a number of useful cmake variables:

* **FIPS\_POSIX**: target platform is UNIX-ish (basically anything but Windows)
* **FIPS\_WINDOWS**: target platform is Windows
* **FIPS\_OSX**: target platform is OSX-ish (either OSX 10.x or iOS) 
* **FIPS\_CLANG**: C++ compiler is clang
* **FIPS\_GCC**: C++ compiler is GCC
* **FIPS\_MSVC**: C++ compiler is Visual Studio compiler
* **FIPS\_LINUX**: target platform is Linux
* **FIPS\_MACOS**: target platform is OSX 10.x
* **FIPS\_IOS**: target platform is iOS
* **FIPS\_WIN32**: target platform is 32-bit Windows
* **FIPS\_WIN64**: target platform is 64-bit Windows
* **FIPS\_EMSCRIPTEN**: target platform is emscripten
* **FIPS\_ANDROID**: target platform is Android
* **FIPS\_HOST\_WINDOWS**: host platform is Windows
* **FIPS\_HOST\_OSX**: host platform is OSX
* **FIPS\_HOST\_LINUX**: host platform is Linux
* **FIPS\_ROOT\_DIR**: absolute path of the fips root directory
* **FIPS\_PROJECT\_DIR**: absolute path of the current project
* **FIPS\_DEPLOY\_DIR**: absolute path of the deployment directory
* **FIPS\_CONFIG**: name of the current build configuration (e.g. osx-xcode-debug)
* **FIPS\_IMPORT**: set inside import CMakeLists.txt files

### Fips CMake Options

Fips provides a few build options which can be tweaked by running **./fips config**
(requires the ccmake or cmake-gui tools to be in the path).

Besides _./fips config_, cmake options can also be provided in
a build config YAML file, for instance the following config file
sets the FIPS\_UNITTESTS and FIPS\_UNITTESTS\_HEADLESS options to ON:

```yaml
---
platform: emscripten 
generator: Ninja 
build_tool: ninja
build_type: Debug
defines:
    FIPS_UNITTESTS: ON
    FIPS_UNITTESTS_HEADLESS: ON
```

### CMakeLists.txt Samples

Here's a very simple root CMakeLists.txt file from the _fips-hello-world_
sample project:

```cmake
cmake_minimum_required(VERSION 2.8)
project(fips-hello-world)

# include the fips main cmake file
get_filename_component(FIPS_ROOT_DIR "../fips" ABSOLUTE)
include("${FIPS_ROOT_DIR}/cmake/fips.cmake")

fips_project(fips-hello-world)
fips_add_subdirectory(src)
fips_finish()
```

The _src_ subdirectory contains the CMakeLists.txt file which defines
the actual appliction:

```cmake
fips_begin_app(hello cmdline)
    fips_files(hello.cc)
    fips_deps(dep1)
fips_end_app()
```

This is a more complex root CMakeLists.txt file from the Oryol 3D engine:

```cmake
#----------------------------------------------------------
#	oryol cmake root file
#
#	See BUILD.md for details how to build oryol.
#----------------------------------------------------------
cmake_minimum_required(VERSION 2.8)
project(oryol)

get_filename_component(FIPS_ROOT_DIR "../fips" ABSOLUTE)
include("${FIPS_ROOT_DIR}/cmake/fips.cmake")

option(ORYOL_SAMPLES "Build Oryol samples" ON)

include_directories(code)
include_directories(code/Modules)
include_directories(code/Ext)

fips_setup()
fips_add_subdirectory(code/Hello)
fips_ide_group(Modules)
fips_add_subdirectory(code/Modules)
fips_ide_group(Ext)
fips_add_subdirectory(code/Ext)
if (ORYOL_SAMPLES)
   fips_ide_group(Samples)
   fips_add_subdirectory(code/Samples)
endif()
fips_finish()
```

Next a sample which defines a code module with platform-specific source
code in subdirectories, and towards the end some dependencies to other
fips modules:

```cmake
#----------------------------------------------------------
#   oryol Input module
#----------------------------------------------------------
fips_begin_module(Input)
    fips_files(Input.cc Input.h)
    fips_dir(Core)
    fips_files(
        CursorMode.h
        Gamepad.cc Gamepad.h
        InputSetup.h
        Key.cc Key.h
        Keyboard.cc Keyboard.h
        Mouse.cc Mouse.h
        Sensors.h
        Touchpad.cc Touchpad.h
        inputMgr.h
    )
    fips_dir(base)
    fips_files(inputMgrBase.cc inputMgrBase.h)
    fips_dir(touch)
    fips_files(
        gestureState.h
        panDetector.cc
        panDetector.h
        pinchDetector.cc
        pinchDetector.h
        tapDetector.cc
        tapDetector.h
        touchEvent.cc
        touchEvent.h
    )
    if (FIPS_ANDROID)
        fips_dir(android)
        fips_files(androidInputMgr.cc androidInputMgr.h)
    endif()
    if (FIPS_EMSCRIPTEN)
        fips_dir(emsc)
        fips_files(emscInputMgr.cc emscInputMgr.h)
    endif()
    if (FIPS_IOS)
        fips_dir(ios)
        fips_files(iosInputMgr.cc iosInputMgr.h)
    endif()
    if (FIPS_MACOS OR FIPS_WINDOWS OR FIPS_LINUX)
        fips_dir(glfw)
        fips_files(glfwInputMgr.cc glfwInputMgr.h)
        fips_deps(glfw3)
    endif()
    fips_deps(Core Gfx Time)
fips_end_module()
```

Finally an example how to wrap a simple C library with a few custom
C preprocessor defines:

```cmake
fips_begin_lib(zlib)
    fips_files(
        adler32.c
        compress.c
        crc32.c crc32.h
        deflate.c deflate.h
        infback.c 
        inffast.c inffast.h
        inffixed.h
        inflate.c inflate.h
        inftrees.c inftrees.h
        trees.c trees.h
        uncompr.c
        zconf.h
        zlib.h
        zutil.c zutil.h
    )
    add_definitions(-D_NO_FSEEKO)
    add_definitions(-D_CRT_SECURE_NO_DEPRECATE)
    add_definitions(-D_CRT_NONSTDC_NO_DEPRECATE)
fips_end_lib(zlib)
```
