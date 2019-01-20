---
layout: page
title: About Fips
permalink: index.html
---

# fips is like Vagrant, but for cmake.

Fips simplifies working with many different cmake build configurations just
like Vagrant simplifies working with many different Virtual Machine
configurations.

### Feature Overview

Fips is a Python tool which provides an 'Integrated Build Environment'
on the command line for multi-platform, modular C/C++ projects by wiring
together existing build tools. 

#### An 'Integrated Build Environment"

Fips doesn't reinvent the wheel by implementing yet-another build system
from scratch, but instead wires existing build tools together:

* **cmake** to describe the project structure and generate project files
* **make, ninja, xcodebuild** as command line build tools
* IDE support as provided by cmake (i.e. **Visual Studio, Xcode, QtCreator**)
* **git** to resolve external project dependencies

#### Multi-Platform Support

Fips can build on **Windows, OSX, Linux**, and cross-compile to **iOS,
emscripten** and **Android**. Fips also takes care of installing 
the cross-platform SDKs and provides a unified cmake build environment 
for all target platforms. Instead of wrestling with the many different build
systems used by those cross-platform SDKs you only maintain a single set 
of cmake files for all target platforms.

#### Build Configuration Management

Multi-platform projects often have dozens of different build configurations
for combinations of target platforms, build tools and build settings.
Fips makes it easy to work with many different build configurations, and
keeps the build files for each configuration separated from each other.

#### Dependency Management

Fips projects can define exports and imports to and from other fips projects,
and thus serve as a simple package manager for code modules. External
projects will be pulled in via git and fips will import external build targets,
and setup header and library search paths. A project with external dependencies
will look and feel exactly the same like a completely local project.

#### Code Generation

Fips implements a simple yet powerful code generation mechanism by calling
Python 'generator scripts' during the build process.

#### Extensible

Fips projects can implement their own fips commands, build configurations and
code generator scripts. This allows projects to implement missing
fips features and integrate fips with existing workflows and build processes.


### What fips is not:

- fips is not a build job scheduler like Jenkins, Hudson, msbuild or ant
- fips is not a distributed build system like Incredibuild
- fips is not a replacement for cmake, premake or scons
- fips is not a game asset exporter pipeline

