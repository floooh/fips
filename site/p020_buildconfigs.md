---
layout: page
title: Build Configs
permalink: buildconfigs.html
---

### About build configs

A build config describes how cmake should generate build system files:

* what **target platform** to compile to (e.g. OSX, Linux, emscripten, ...)
* what **build tool or IDE** to use (e.g. make, ninja, VStudio, Xcode...)
* what **build type** to compile (Release, Debug, Profiling...)
* what additional **cmake options** to use for tweaking the build

Build configs have a unique, descriptive name, e.g.:

* osx-xcode-debug
* linux-make-debug
* android-make-debug

The build config name resolves to a small YML file in the _fips/configs_
directory, for instance the _android-make-debug_ config lives in the file 
_fips/configs/android-make-debug.yml_ and looks like this:

```
---
platform: android
generator: Unix Makefiles
build_tool: make
build_type: Debug
defines:
    ANDROID_CPU: arm
    ANDROID_API: android-19
```

Fips keeps all build files separate from each other by config name, building
a project for one config will not overwrite the build files of other configs.


#### Listing available configs

The currently available standard configs can be shown with the 
'fips list configs' command from within the fips directory:

```bash
> ./fips list configs
=== configs:
from /Users/floh/projects/fips/configs:
  android-make-debug
  android-make-release
  androidmips-make-debug
  ...
  pnacl-ninja-debug
  pnacl-ninja-release
> _
```

When 'fips list configs' is executed inside a project directory, it will
also list any custom configs defined by that project. For instance from
inside the Oryol directory:

```bash
> ./fips list configs
=== configs:
from /Users/floh/projects/fips/configs:
  android-make-debug
  android-make-release
  ...
from /Users/floh/projects/oryol/fips-configs:
  oryol-emsc-unittest
> _
```

Note the custom config called _oryol-emsc-unittest_ at the end of the list.

#### Config names

There are no naming conventions for configs, so custom configs can have any
name that doesn't clash with a standard config name.

The standard config names are usually made of 3 parts separated by 
dashes to be as self-descriptive as possible:

1. the target platform (e.g. osx, linux, win32)
2. the build tool (e.g. make, ninja, vstudio, ...)
3. the build type (e.g release, debug, ...)

> [platform]-[buildtool]-[buildtype]

For instance:

**osx-xcode-debug** means: target platform is OSX, the build tool is Xcode,
and the Debug version should be built (with debug info and no optimizations)

#### Default configs

Every host platform has a default config which is used when no config name
is provided:

* **Linux**: linux-make-debug
* **OSX**: osx-xcode-debug
* **Windows**: win64-vstudio-debug

#### Active config

To save typing, an _active config_ can be set per project with 
**fips set config [config]**, this active config is used when a fips command
expects a config name, but none is given. 

The active config can be unset with **fips unset config**.

Finally, the currently active config can be displayed with **fips list settings**

For instance in a fips project:

```bash
# first check that now active config is set:
> ./fips list settings
=== settings:
  config: osx-xcode-debug (default value)
  target: None (default value)

# if no config is currently set, the default config is used:
> ./fips gen
=== generating: osx-xcode-debug
...

# now set a different 'active config' 
> ./fips set config osx-make-debug
'config' set to 'osx-make-debug' in project 'oryol'
> ./fips list settings
=== settings:
  config: osx-make-debug
  target: None (default value)

# when no config is given, the 'active config' will now be used
> ./fips gen
=== generating: osx-make-debug
...

# it's possible to override the active config:
> ./fips gen emsc-make-debug
=== generating: emsc-make-debug
...

# unset the active config, so that it switches back to the default config:
> ./fips unset config
'config' unset in project 'oryol'
> ./fips list settings
=== settings:
  config: osx-xcode-debug (default value)
  target: None (default value) 
```

#### Commands using config names 

The following fips commands expect a config name (excerpt from 'fips help'):

```bash
fips build
fips build [config]
   perform a build for current or named config

fips clean
fips clean all
fips clean [config]
    clean generated build files for config

fips config
fips config [config]
   configure the current or named build config
   (runs ccmake or cmake-gui)

fips gen
fips gen [config]
    generate build files for current or named config

fips make
fips make [target]
fips make [target] [config]
   build a single target in current or named config

fips open
fips open [config]
   open IDE for current or named config

fips run
fips run [target]
fips run [target] [config]
   run a build target for current or named config
```


#### Project-specific custom configs

A fips project can define its own configs in a special subdirectory
called _fips-configs_. As an example, check the Oryol project directory
(https://github.com/floooh/oryol.git):

```bash
> cd oryol
> cd fips-configs
> ls
oryol-emsc-unittest.yml
> cat oryol-emsc-unittest.yml
# this demonstrates how to add a custom config to fips projects
# usually you'll want to tweak cmake-options with such
# custom settings
---
platform: emscripten
generator: Ninja
build_tool: ninja
build_type: Debug
defines:
    FIPS_UNITTESTS: ON
    FIPS_UNITTESTS_HEADLESS: ON
> _
```

