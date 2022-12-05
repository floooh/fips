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

#### fips\_ide\_group(name)

Start a new project explorer folder in an IDE. This can be used to
group related build targets for a clearer layout in the IDE's project
explorer.

#### fips\_begin\_lib(name)

Begin defining a static link library. A fips library is a collection of source
files that compile into a static link library.

After a fips\_begin\_lib() the following fips macros are valid:

* fips\_dir()
* fips\_files()
* fips\_generate()
* fips\_deps()
* fips\_libs()
* fips\_end\_lib()

fips_begin_lib() creates a cmake target, this means you can also call any of
the ```target_*``` cmake commands inside fips_begin_lib()/fips_end_lib.

#### fips\_end\_lib()

This finishes a fips\_begin\_lib() block.

#### fips\_begin\_sharedlib(name)

Begin defining a fips shared library. A fips shared library is a collection of source
files that compile into a dynamically linkable library (as opposed to static libraries).

After a fips\_begin\_sharedlib() the following fips macros and cmake commands are valid:

* fips\_dir()
* fips\_files()
* fips\_generate()
* fips\_deps()
* fips\_libs()
* fips\_end\_sharedlib()

fips_begin_sharedlib() creates a cmake target, this means you can also call any of
the ```target_*``` cmake commands inside fips_begin_sharedlib()/fips_end_sharedlib.

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

As with the other begin/end macros, the cmake ```target_*``` commands can
be called within a begin/end block.

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

#### fips\_libs(libs ...)
#### fips\_deps(dep ...)

Adds static link library dependencies to the current build target.

fips_deps is an alias of fips_libs, and fips_libs is an alias for
```target_link_libraries(${target} ${libs})```.

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
cmake_minimum_required(VERSION 3.21)
project(fips-hello-world)

# include the fips main cmake file
get_filename_component(FIPS_ROOT_DIR "../fips" ABSOLUTE)
include("${FIPS_ROOT_DIR}/cmake/fips.cmake")
fips_setup()

add_subdirectory(src)
```

The _src_ subdirectory contains the CMakeLists.txt file which defines
the actual appliction:

```cmake
fips_begin_app(hello cmdline)
    fips_files(hello.cc)
    fips_deps(dep1)
fips_end_app()
```

...and the 'dep1' dependency could look like this:

```cmake
fips_begin_lib(dep1)
    fips_files(dep1.cc)
fips_end_lib()
```

...libraries can themselve have dependencies, those are then resolved in the
correct order in the executable target link step:

```cmake
fips_begin_lib(dep1)
    fips_files(dep1.cc)
    fips_deps(dep2)
fips_end_lib()
```

Vanilla cmake target-commands can be placed inside the begin/end:

```cmake
fips_begin_lib(dep1)
    fips_files(dep1.cc)
    fips_deps(dep2)
    # disable some MSVC specific warnings:
    if (FIPS_MSVC)
        target_compile_options(dep1 PRIVATE /wd4312)
    endif()
fips_end_lib()
```
