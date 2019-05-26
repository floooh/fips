---
title: "Exports"
weight: 7
# bookFlatSection: false
# bookShowToC: true
---
# Exporting from fips projects

A fipsified project can provide different types of 'exports' to other
fips projects:

* code modules
* header search paths
* pre-compiled static libs
* C/C++ preprocessor defines
* a cmake include which is included in root CMakeLists.txt files of importing projects
* new fips commands
* build configs
* code generator scripts

### Exporting Code Modules

Projects can export modules defined with the fips\_begin\_module() and
fips\_begin\_lib() commands in under the 'exports' section of the fips.yml
file. 

For instance, here are the exported modules of the Oryol 3D engine:

```yaml
exports:
    modules :
        # engine modules
        Core :          code/Modules/Core
        IO :            code/Modules/IO
        Messaging :     code/Modules/Messaging
        HTTP :          code/Modules/HTTP
        Gfx :           code/Modules/Gfx
        Resource :      code/Modules/Resource
        Assets :        code/Modules/Assets
        Time :          code/Modules/Time
        Dbg :           code/Modules/Dbg
        Input :         code/Modules/Input
        Synth :         code/Modules/Synth
        NanoVG :        code/Modules/NanoVG
        
        # ext libs
        ConvertUTF:         code/Ext/ConvertUTF
        android-native:     code/Ext/android_native
        flextgl:            code/Ext/flextgl
```

The 'value' in the modules export dictionary is the directory where the
CMakeLists.txt file of the module lives, relative to the project root directory.

The 'key' value must be identical with the name of the module defined in the
CMakeLists.txt file.

### Exporting Header Search Paths

Projects can export a list of header search paths in their fips.yml file which 
are then defined in  the toplevel CMakeLists.txt file of the importing project 
and are visible to the entire project:

```yaml
exports:
    header-dirs :
        - code
        - code/Modules
        - code/Ext
```

Of course it is also possible to directly use 'fips\_include\_directories()'
or 'include\_directories()' in imported CMakeLists.txt files, but be aware
that these only propagate downwards in the CMakeLists.txt hierarchy, not
upwards.

### Exporting Precompiled Static Libs

Exporting precompiled static libs works a bit differently, they are not
defined in the fips.yml file, instead fips checks if the imported project
has a 'libs' directory. If yes, library search paths are automatically
added in the importing project, so that the imported libs are found
automatically by fips\_libs().

Static link libs need to be located in subdirectories of 'libs' named
after the target platform the libs are compiled for:

```
┗━━ fips-sdks/
    ┗━━ osx/
    ┗━━ win32/
    ┗━━ win64/
    ┗━━ linux/
    ┗━━ emscripten/
    ┗━━ ios/
    ┗━━ android/
```

There's no directory separation for release and debug versions of precompiled
libs. If you need this, it must be handled through differently named libs
(e.g. a \_d postfix for debug libs).

> NOTE: the way how static library imports are defined may change in the
future (moving them into the fips.yml file)

### Exporting C/C++ Preprocessor Defines

Projects can list C/C++ preprocessor defines as key/value pairs in the
export section of the fips.yml file. These defines are visible in the
entire CMakeLists.txt hierarchy of the importing project. Here's an 
example from fips-glm to set the angle unit to radians:

```yaml
exports :
    defines :
        GLM_FORCE_RADIANS : 1
```

For finer control (e.g. define different defines for different platforms)
it is better to directly use cmake add\_defines() statements in the
fips-include.cmake file (discussed below).

### The fips-include.cmake File

Projects can place an optional fips-include.cmake file into their 
root directory with additional cmake statements. This file is both
included when building the project directory, as well as in the
toplevel CMakeLists.txt file of importing projects. Have a look
at Oryol's fips-include.cmake file for an example:

https://github.com/floooh/oryol/blob/master/fips-include.cmake

### Adding New Fips Commands

Projects can have an optional directory 'fips-files/verbs' containing
python scripts which add new subcommands (== verbs) to fips. The
name of the python script (without the .py) is the name of the 
command, and the script must define two special functions **help** 
and **run**:

* **help()**: this is called when 'fips help' is invoked, should print 
a help message formatted like the other builtin help messges
* **run(fips\_dir, proj\_dir, args)**: contains the actual logic of the 
command. The args fips\_dir and proj\_dir are the absolute paths 
to the fips directory and the project directory where the command
is run from. Args is a string array of all arguments given to the
command.

As an example, have a look at Oryol's 'webpage' command here:

https://github.com/floooh/oryol/blob/master/fips-files/verbs/webpage.py

### Build Configs

Projects can define new build configs which extend fips' builtin
configs. These build config files must be located in a subdirectory
called 'fips-files/configs'.

Again, here's are example configs in the Oryol engine:

https://github.com/floooh/oryol/tree/master/fips-files/configs

### Code Generator Scripts

Projects can extend fips with code generation python scripts in the
'fips-files/generators' subdirectory. The details are described on the
[Code Generation Page](/fips/codegen.html).

