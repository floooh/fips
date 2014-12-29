### About fips build configs

**WORK IN PROGRESS**

Build configs are YML files which describe how cmake should generate build
files. Fips comes with a number of standard config files, and fips projects
can define their own configs.

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
  androidmips-make-release
  androidx86-make-debug
  androidx86-make-release
  emsc-make-debug
  emsc-make-release
  emsc-ninja-debug
  emsc-ninja-release
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
name. 

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
[TODO]

#### Sample commands
[TODO]

#### Config file content
[TODO]

#### Project custom configs
[TODO]
