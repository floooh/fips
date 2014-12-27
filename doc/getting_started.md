### Getting Started with fips

This is a step-by-step guide from installing fips to building a
sample 'Hello World' project.

#### You need:

* Python 2.7.x
* CMake (at least version 2.8.11)
* a working C/C++ development environment for your OS (e.g. Xcode on OSX,
make/gcc on Linux, Visual Studio on Windows)

#### Setting up and testing fips:

Clone the fips git repo into a separate directory, and check if the 
fips main script runs.

>NOTE: on Windows, run 'fips' instead of './fips'! 

```bash
> cd ~
> mkdir fips-workspace
> cd fips-workspace
> git clone https://github.com/floooh/fips.git
...
> cd fips
> ./fips
run 'fips help' for more info
> _
```

#### Showing help:

Run 'fips help' to get an overview of available commands:

```bash
> ./fips help
fips: the high-level, multi-platform build system wrapper
v0.0.1
https://www.github.com/floooh/fips

fips build
fips build [config]
   perform a build for current or named config
...
fips unset config
fips unset target
    unset currently active config or make-target

> _
```

You can show help for a specific command:

```bash
> ./fips help diag
fips diag
fips diag all
fips diag tools
fips diag configs
fips diag imports
    run diagnostics and check for errors
```

#### Check if required tools are installed

Run 'fips diag tools' to check whether the required command line
tools are found by fips:

```bash
> ./fips diag tools
=== tools:
git:    found
cmake:    found
ccmake:    found
make:    found
ninja:    NOT FOUND
xcodebuild:    found
```

Install any tools which are shown as 'NOT FOUND'.

#### Clone the sample project

List the fips project registry, and clone the 'Hello World' sample
project and its dependencies:

```bash
> ./fips list registry
=== registry:
...
fips-hello-world => https://github.com/floooh/fips-hello-world.git
...
```

Clone the 'fips-hello-world' sample project. It's dependencies will also
automatically be cloned from github:

```bash
> ./fips clone fips-hello-world
registry lookup: fips-hello-world => https://github.com/floooh/fips-hello-world.git
Cloning into 'fips-hello-world'...
remote: Counting objects: 66, done.
remote: Compressing objects: 100% (14/14), done.
remote: Total 66 (delta 3), reused 0 (delta 0)
Unpacking objects: 100% (66/66), done.
Checking connectivity... done.
=== dependency: 'fips-hello-dep1':
Cloning into 'fips-hello-dep1'...
remote: Counting objects: 64, done.
remote: Compressing objects: 100% (6/6), done.
remote: Total 64 (delta 1), reused 0 (delta 0)
Unpacking objects: 100% (64/64), done.
Checking connectivity... done.
=== dependency: 'fips-hello-dep2':
Cloning into 'fips-hello-dep2'...
remote: Counting objects: 60, done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 60 (delta 0), reused 0 (delta 0)
Receiving objects: 100% (60/60), 7.49 KiB | 0 bytes/s, done.
Resolving deltas: 100% (15/15), done.
Checking connectivity... done.
> _
```

#### Build and run the fips-hello-world project:

fips sample projects live side-by-side next to the fips directory,
a fips project can be built by cd'ing to it, and running './fips build':

```bash
> cd ../fips-hello-world
> ./fips build
=== dependency: 'fips-hello-dep1':
dir '/Users/floh/fips-workspace/fips-hello-dep1' exists
=== dependency: 'fips-hello-dep2':
dir '/Users/floh/fips-workspace/fips-hello-dep2' exists
=== building: osx-xcode-debug
=== generating: osx-xcode-debug
-- The C compiler identification is AppleClang 6.0.0.6000056
-- The CXX compiler identification is AppleClang 6.0.0.6000056
-- Check for working C compiler using: Xcode
-- Check for working C compiler using: Xcode -- works
...
** BUILD SUCCEEDED **

1 configs built
> _
```

Now run the compiled 'hello' executable:

```bash
> ./fips run hello
=== run 'hello' (config: osx-xcode-debug, project: fips-hello-world):
Hello World!
Hello from dep1
Hello from dep2!
Imported string define: Bla
Imported int define: 1
> _
```

#### Working with build configs

A build config describes how to build a project for different 
platforms, build tools and build modes. Run 'fips list configs' to see
a list of available configs:

```bash
> fips list configs
=== configs:
/Users/floh/fips-workspace/fips:
  android-make-debug
  android-make-release
  androidmips-make-debug
  androidmips-make-release
  androidx86-make-debug
  androidx86-make-release
  emsc-make-debug
  emsc-make-release
...
  osx-xcode-unittest
  pnacl-make-debug
  pnacl-make-release
  pnacl-ninja-debug
  pnacl-ninja-release
> _
```

There is no hard rule for build config names, but usually they are made
from 3 parts, first the target platform name (e.g. osx, linux, win32), 
then the build tool (e.g. make, xcode, vstudio) and the build mode (e.g.
debug, release).

Not all build configs are supported on a given host platform, for instance it
is not possible to build for iOS on Windows or Linux platforms.

It is possible to select a build config when building, for instance on 
OSX it is possible to use make instead of xcodebuild, the build result
is the same, but the console output looks prettier:

```bash
> ./fips build osx-make-release
=== dependency: 'fips-hello-dep1':
dir '/Users/floh/fips-workspace/fips-hello-dep1' exists
=== dependency: 'fips-hello-dep2':
dir '/Users/floh/fips-workspace/fips-hello-dep2' exists
=== building: osx-make-debug
=== generating: osx-make-debug
-- The C compiler identification is AppleClang 6.0.0.6000056
...
> _
```

