---
title: Introduction
type: docs
bookShowToC: true
---

# What is Fips

Fips is a Python command line tool which provides an 'Integrated Build
Environment' for C/C++ projects by wiring together existing build tools. It
enables a workflow similar to Rust's Cargo or Javascript's NPM, but for C/C++
projects.

## An 'Integrated Build Environment'

Fips doesn't reinvent the wheel by implementing yet-another build system
from scratch, but instead wires existing build tools together:

* **cmake** to describe the project structure and generate project files
* **make, ninja, xcodebuild** as command line build tools
* IDE support as provided by cmake (i.e. **Visual Studio, Xcode, VSCode**)
* **git** to fetch external dependencies
* **python** to extend fips with new commands and code-generation-scripts

## Multi- and Cross-Platform Support

Fips can build on **Windows, OSX, Linux**, and cross-compile to **iOS,
emscripten** and **Android**. Fips also takes care of installing 
the cross-platform SDKs and provides a unified cmake build environment 
for all target platforms. Instead of wrestling with the many different build
systems used by those cross-platform SDKs you only maintain a single set 
of cmake files for all target platforms.

## Build Configuration Management

Cross-platform projects often have dozens of different build configurations
for combinations of target platforms, build tools and build settings.
Fips makes it easy to work with many different build configurations, and
keeps the build files for each configuration separated from each other.

## Dependency Management

Fips projects can define exports and imports to and from other fips projects,
and thus serve as a simple package manager for code modules. External
projects will be pulled in via git and fips will import external build
targets, fips commands, code-generators and setup header and library search
paths. A project with external dependencies will look and feel exactly the
same like a completely local project.

## Code Generation

Fips implements a simple yet powerful code generation mechanism by calling
Python 'generator scripts' during the build process.

## Extensible

Fips projects can implement their own fips commands, build configurations and
code generator scripts. This allows projects to implement missing
fips features and integrate fips with existing workflows and build processes.

# What Fips is not:

- fips is not a build job scheduler like Jenkins, Hudson, msbuild or ant
- fips is not a distributed build system like Incredibuild
- fips is not a replacement for cmake, premake or scons


