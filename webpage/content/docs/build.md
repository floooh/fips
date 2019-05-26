---
title: "Build Projects"
weight: 2
---
# Build Projects

To build the default build configuration of a 'fipsified' project for your 
host platform, simply run './fips build' in its root directory:

```
> cd ~/fips-workspace
> git clone https://github.com/floooh/fips-hello-world.git
> cd fips-hello-world
> ./fips build
...
> _
```

By default, a non-optimized _debug_ version will be built, to build
an optimized _release_ version append the configuration name that is 
right for your host platform:

```
# on OSX:
> ./fips build osx-xcode-release
...
# on Linux:
> ./fips build linux-make-release
...
# on Windows:
> ./fips build win64-vstudio-release
...
> _
```

### Build Configs

Build configs like _osx-xcode-release_ are the core feature of fips. A
build config tells cmake how to compile the project:

* the **target platform** to build for
* the **build tool** to use
* the **build type** (e.g. debug or release)
* additional cmake options to customize a build

To get a list of build configurations, run './fips list configs':

```
> ./fips list configs
from /Users/floh/projects/fips/configs:
  android-make-debug
  android-make-release
  android-ninja-debug
  android-ninja-release
...
  win32-vstudio-debug
  win32-vstudio-release
  win64-vstudio-debug
  win64-vstudio-release
> _
```

There are dozens of build configs, but not all are supported on every
host platform, to test which build configs are supported, run 
'./fips diag configs':

```
> ./fips diag configs
=== configs:
android-make-debug
  ok
android-make-release
  ok
android-ninja-debug
  build tool 'ninja' not found
android-ninja-release
  build tool 'ninja' not found
...
> _
```

In this example, the build configurations which use the 'ninja' build tool
can not be used because ninja is currently not installed (see also './fips
diag tools').

### Active Config

To save typing, an _active config_ can be set per project. This will
be used if a fips command expects a config name, but none is given. 
Use './fips set config [config-name]' if you
want to compile the release version of a project instead of the default
debug version whenever './fips build' is run:

```
# on OSX:
> ./fips set config osx-xcode-release
'config' set to 'osx-xcode-release' in project 'fips-hello-world'
> ./fips build
...
# on Linux:
> ./fips set config linux-make-release
'config' set to 'linux-make-release' in project 'fips-hello-world'
> ./fips build
...
# on Windows:
> ./fips set config win64-vstudio-release 
'config' set to 'win64-vstudio-release' in project 'fips-hello-world'
> ./fips build
...
> _
```

Run './fips list settings' to check what the currently active config is:

```
> ./fips list settings
=== settings:
  config: osx-xcode-release
  target: None (default value)
```

To revert back to the default config, run './fips unset config':

```
> ./fips unset config
'config' unset in project 'fips-hello-world'
> ./fips list settings
=== settings:
  config: osx-xcode-debug (default value)
  target: None (default value)
> _
```

### Build Targets

Projects are usually made of several build targets, of which fips has 3
types:

* **apps**: statically linked applications
* **modules**: high level static libraries with dependencies to other modules
* **libs**: low-level static libraries, usually 3rd party code with custom compile
settings

The targets a project is made of and their dependencies are described
in CMakeLists.txt files. This is a complex topic for later. For now let's just
see how to list the targets of a project, and how to build and run specific
targets.

To get a list of targets in the current project, run './fips list targets'
from the project root directory. For this to work, cmake must have generated 
build files before via './fips gen':

```
> ./fips gen
...
> ./fips list targets
=== targets:
  config: osx-xcode-debug
  lib:
  module:
    dep1
    dep2
  app:
    hello
> _ 
```

A specific target can be built with './fips make [target]':

```
> ./fips make hello
...
> _
```

App targets can be run with './fips run [target]':

```
> ./fips run hello
=== run 'hello' (config: osx-xcode-debug, project: fips-hello-world):
Hello World!
Hello from dep1
Hello from dep2!
Imported string define: Bla
Imported int define: 1
> _
```
