---
title: "Get Started"
weight: 1
# bookFlatSection: false
# bookShowToC: true
---

# Get Started

### You need:

* python (2.7.x or 3.x should both work)
* cmake (any 3.x version should work)
* a working C/C++ development environment:
    * on **OSX**: Xcode + command line tools
    * on **Linux**: make/gcc (or clang)
    * on **Windows**: Visual Studio 2013 or better

### Get fips

fips will create additional directories on the same directory level as
the fips directory itself, thus it is recommended to git-clone fips into a separate
'workspace' directory:

```
> cd ~
> mkdir fips-workspace
> cd fips-workspace
> git clone https://github.com/floooh/fips.git
> cd fips
> _
```


### Test if fips works

Invoke the fips main script by running './fips' from within the fips directory:

> NOTE: on Windows, run 'fips' instead of './fips'

```
> ./fips
run 'fips help' for more info
```

> NOTE: usually './fips' is run from the root directory of a 'fipsified' C/C++
project, not from the fips directory

### Get help

Run './fips help' to show available fips commands:

```
> ./fips help
fips: the high-level, multi-platform build system wrapper
v0.0.1
https://www.github.com/floooh/fips

fips build
fips build [config]
   perform a build for current or named config
...
> _
```

You can also show help for a single command:

```
> ./fips help diag
fips diag
fips diag all
fips diag fips
fips diag tools
fips diag configs
fips diag imports
    run diagnostics and check for errors
> _
```

### Get required tools

Run './fips diag tools' to check for required tools, install any that are
listed as 'NOT FOUND'. The list of required tools may differ depending on 
your host platform.

```
> ./fips diag tools
=== tools:
git:	found
cmake:	found
ccmake:	found
make:	found
ninja:	OPTIONAL, NOT FOUND (required for building '*-ninja-*' configs)
xcodebuild:	found
java:	found
ant:	found
python2:	found
> _
```

> NOTE that some tools are optional and only required for specific 
build configurations

### Setup new project

A new fips project can be setup by running './fips init path/to/project'. This will copy a few commonly used fips config files into the target project directory. From the fips directory run './fips init project-1' and the following will be setup for you:

```
┗━━ fips-workspace/
    ┗━━ fips/
    ┃   ┗━━ ...
    ┗━━ project-1/
        ┣━━ fips.yml 
        ┣━━ fips 
        ┣━━ fips.cmd 
        ┣━━ CMakeLists.txt 
        ┗━━ .gitignore
```

> NOTE fips will look for the folder in the root of the fipsified project (in this case the fips-workspace created above) and not in the fips folder itself. 

From now on you can run all fips commands directly in the new project's directory.

