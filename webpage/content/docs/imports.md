---
title: "Imports"
weight: 6
# bookFlatSection: false
# bookShowToC: true
---
# Importing external dependencies

fips implements a very simple 'package manager' for external code modules. A
fips project can list a number of 'imports' in its fips.yml file to import
external projects. A project which uses external dependencies
will look and feel the same as if all dependencies would reside locally in
the main project.

Importing external projects has a number of advantages (and one notable 
disadvantage):

- generic libraries live in their own github repositories and can easily be
  shared by many projects
- ownership is clearly defined, the owner of an imported project is the
  owner of the git repository which contains the imported project
- if dependency trees become too complex, the result might be 'dependency hell'
  where version conflicts occur when imported projects depend on different
  versions of another project

Care should be taken when working with external dependencies to keep the
dependency tree reasonably shallow. Do not split a project into too many,
too granular sub-projects.

### Fipsification

fips can only import projects that have at least a fips.yml in their
project root, and thus has been 'fipsified'. The details and
different ways of 'fipsification' are described on the **Exports** 
documentation page, for now it is only important to know that the silly term 
'fipsified project' means a project that has been made compatible with 
fips.

### How to define imports

Simply list imports in your fips.yml file under the section 'imports'.

Here is a very simple example from the _fips-hello-world_ project:

```yaml
---
imports:
    fips-hello-dep1:
        git:    https://github.com/floooh/fips-hello-dep1.git
```

This defines a single import _fips-hello-dep1_ from the github URL 
_https://github.com/floooh/fips-hello-dep1.git_.

Dependencies can be recursive, for instance the _fips-hello-dep1_
project imports another project:

```yaml
---
imports:
    fips-hello-dep2:
        git:    https://github.com/floooh/fips-hello-dep2.git
```

A more complex import section might look like this (from the Oryol 3D engine):

```yaml
---
imports:
    gliml:
        git: https://github.com/floooh/gliml.git
    fips-glm:
        git: https://github.com/floooh/fips-glm.git
    fips-unittestpp:
        git: https://github.com/floooh/fips-unittestpp.git
    fips-zlib:
        git: https://github.com/floooh/fips-zlib.git
    fips-glfw:
        git: https://github.com/floooh/fips-glfw.git
    fips-libcurl:
        git: https://github.com/floooh/fips-libcurl.git
```

In the future there will be more ways to define imports, 
most likely support for more version control systems like Subversion
or Mercurial.

### Importing specific versions

It is possible to specify a git branch, tag name or revision when defining an import
in fips.yml. This is usually a good idea for complex real-world projects 
since it prevents that a build suddenly breaks because an external dependency
has had an update that breaks existing code:

```yaml
---
imports:
    my-awesome-lib:
        git: https://github.com/floooh/my-awesome-lib.git
        branch: version-0.0.1
    my-other-awesome-lib:
        git: https://github.com/floooh/my-other-awesome-lib.git
        rev: 00f1a6d3
```

The 'branch:' item can either be a branch or tag name.
The 'rev:' item should be a valid commit SHA1 reference.

### Conditional Imports

An import can contain a conditional cmake-expression which must be true
for the import to happen. For instance to ignore an import on IOS:

```yaml
---
imports:
    my-awesome-lib:
        git: https://github.com/floooh/my-awesome-lib.git
        cond: "NOT FIPS_IOS"
```

The resulting cmake code to import this dependency will then be surrounded
with:

```yaml
if (NOT FIPS_IOS)
    ...actual import code
endif()
```

### Fetching imports

To fetch external dependencies simply run './fips fetch' from within
the project directory which defines the imports:

```
> ./fips fetch
[WARNING] project dir '/Users/floh/projects/fips-hello-dep1' does not exist
=== dependency: 'fips-hello-dep1':
Cloning into 'fips-hello-dep1'...
remote: Counting objects: 51, done.
remote: Compressing objects: 100% (35/35), done.
remote: Total 51 (delta 13), reused 49 (delta 12)
Unpacking objects: 100% (51/51), done.
Checking connectivity... done.
=== dependency: 'fips-hello-dep2':
Cloning into 'fips-hello-dep2'...
remote: Counting objects: 57, done.
remote: Compressing objects: 100% (36/36), done.
remote: Total 57 (delta 16), reused 56 (delta 15)
Unpacking objects: 100% (57/57), done.
Checking connectivity... done.
> _
```

Dependencies will also be automatically be fetched when running './fips clone',
'./fips gen', './fips build', and './fips make'. So most of the time, dependency
fetching will happen automatically when needed.

### Listing imports

To get an overview of the dependency structure of a project, run './fips list imports':

```
> ./fips list imports
== imports:
project 'fips-hello-world' imports:
  'fips-hello-dep1' from 'https://github.com/floooh/fips-hello-dep1.git' at branch 'master'
project 'fips-hello-dep1' imports:
  'fips-hello-dep2' from 'https://github.com/floooh/fips-hello-dep2.git' at branch 'master'
project 'fips-hello-dep2' imports:
    nothing
```

### Updating imports

Imports can be updated with './fips update', updating means, a 'git pull' and
'git submodule update --recursive' will be run on each import, but **only 
if the git repository has no local changes** (uncommitted or unpushed changes),
otherwise the update for this repo will be skipped (this behaviour prevents 
any unwanted merge commits that could happen in this case during the git pull).

Imports with a pinned revision will work as expected. First the usual update
procedure will happen, then a 'git checkout [rev]' to go to the right
revision.

On its own, fips will never automatically update an import, it must always be
manually invoked by running './fips update'. Also note that the toplevel
directory will not be updated, only the imports.

Fips can tell you if an imported dependency is uptodate (meaning: in
sync with its remote repository on github) with './fips diag imports':

```
> ./fips diag imports
=== imports:
git status of 'fips-hello-dep1':
  uptodate
git status of 'fips-hello-dep2':
  uptodate
```

'./fips diag imports' catches uncommitted changes, changes which are
committed but not pushed, and whether the remote repository is ahead of the 
local repository:

```
=== imports:
git status of 'fips-hello-dep1':
[WARNING] '/Users/floh/projects/fips-hello-dep1' has uncommitted changes:
 M README.md

[WARNING]   '/Users/floh/projects/fips-hello-dep1' is out of sync with remote git repo
git status of 'fips-hello-dep2':
  uptodate
```

```
=== imports:
git status of 'fips-hello-dep1':
[WARNING] '/Users/floh/projects/fips-hello-dep1' branches out of sync:
  master: b02b11f6210263c8be058cd415ed47ff58fa64ae
  origin/master: 3280cfde54dcf7c812ab401e14191815d2d5a342
[WARNING]   '/Users/floh/projects/fips-hello-dep1' is out of sync with remote git repo
git status of 'fips-hello-dep2':
  uptodate
```

There's also a less detailed (but faster) diag option which only checks for
uncommitted or unpushed changes (basically the same check that './fips update'
performs to decide whether it is safe to perform a 'git pull'. To check
the list of imports for local changes, simply call './fips diag local-changes'.

### What's imported

In general, fips imports what the imported project exports. Exports are also
defined in the fips.yml file. Exporting from a project is a bit more complex
then importing, so this is described on its own doc page.

Here's a quick list of what can be imported:

* **fips modules and libs**: projects can define a list of modules and libs
from their own CMakeLists.txt hierarchy to be imported in other projects,
each module/lib directory will also automatically be added to the header 
search path
* **header search paths**: projects can export additional header search paths,
this is especially useful for simple header-only fips projects
* **C preprocessor defines**: a fips file can list a number of key/value pairs
that are handed to the compiler as preprocessor defines
* **library search paths**: fips projects can export pre-compiled
static link libraries 
* **any cmake statements**: for more complex use cases fips projects
may contain an optional file called _fips-include.cmake_ in their root directory
which is included in the top-level CMakeLists.txt file of the importing 
project

Detailed information of how these exports are defined can be found on the
**Exports** doc page.

### Selectively importing modules

By default, fips imports all modules of an imported project. Sometimes this
is overkill when only a few modules from a project are needed. This automatic
import of modules into a build project can be switched off in the importing 
project's fips.yml file using the 'no\_auto\_import' policy. Here is an example
fips.yml file which imports a complex dependency and activates the
no\_auto\_import policy:

```yaml
---
policies:
    no_auto_import: true
imports:
    oryol:
        git: https://github.com/floooh/oryol.git
```

Not automatically importing modules means that imported modules must be listed
manually in the root CMakeLists.txt file. For this, fips has created a cmake
import function for each module called **fips\_import\_PROJECT\_MODULE()**,
where PROJECT is the project name, and MODULE is the module name that should be
imported. Any '-' character in the module or project name must be replaced with
an '\_' (underscore) character (cmake doesn't accept '-' in function names).

Manually importing modules can be a lot of trial and error, because the 
entire dependency chain must be manually imported, it's either all 
or nothing with the 'no\_auto\_import' policy.

Here's a segment from a project's root CMakeLists.txt file with 'no\_auto\_import'
enabled as an example:

```cmake
project(yakc)
fips_setup()

# manual imports
fips_ide_group("Oryol")
fips_import_oryol_Core()
fips_import_oryol_Gfx()
fips_import_oryol_IO()
fips_import_oryol_HTTP()
fips_import_oryol_Messaging()
fips_import_oryol_Input()
fips_import_oryol_IMUI()
fips_import_oryol_Resource()
fips_import_oryol_Assets()
fips_import_oryol_Time()
fips_import_oryol_Synth()
fips_ide_group("Libs")
fips_import_fips_zlib_zlib()
fips_import_fips_glfw_glfw3()
fips_import_oryol_flextgl()
fips_import_oryol_ConvertUTF()
fips_import_fips_imgui_imgui()
fips_import_fips_unittestpp_unittestpp()
fips_ide_group("")

fips_include_directories(.)
```

### Under the hood

#### Fetching

To speed up importing, fetching doesn't clone the entire git repository,
instead git is called like this:

```
> git clone --recursive --branch xxx --single-branch --depth 10 
```

It's recommended to use the https protocol to define git URLs so that
projects can be imported without setting up an SSH key for github,
this is especially useful when running automated builds:

> use **https://github.com/floooh/oryol.git** instead of git@github.com:floooh/oryol.git

If you actually want to work on the imported projects it is better to git-clone them
manually using the git SSH protocol (git@github.com/...).

#### Where are imported projects located

Fips stores all imported projects on the same directory level as the
fips directory itself instead of inside the importing project. This
makes it easier to share imported projects between multiple 
importing projects, and simplifies working with git.

#### How importing works

Project imports are resolved during './fips gen' before
running cmake ('./fips fetch' will only git-clone the projects).

During './fips gen', a hidden file _.fips-imports.cmake_ will be 
created in the importing project's root directory which is included
in the main CMakeLists.txt hierarchy and implements the actual cmake 
import magic. For a simple project like _fips-hello-world_ the file
looks like this (details may change in newer fips versions):

```cmake
#
# generated by 'fips gen', don't edit, don't add to version control!
#
if (EXISTS "/Users/floh/projects/fips-hello-dep2/fips-include.cmake")
    include("/Users/floh/projects/fips-hello-dep2/fips-include.cmake")
endif()
if (EXISTS "/Users/floh/projects/fips-hello-dep2/lib/${FIPS_PLATFORM_NAME}")
    link_directories("/Users/floh/projects/fips-hello-dep2/lib/${FIPS_PLATFORM_NAME}")
endif()
include_directories("/Users/floh/projects/fips-hello-dep2/src")
add_definitions(-DTEST_DEFINE_2="Bla")
add_definitions(-DTEST_DEFINE_1=1)
macro(fips_import_fips_hello_dep2_dep2)
    set(FIPS_IMPORT 1)
    add_subdirectory("/Users/floh/projects/fips-hello-dep2/src/dep2" "fips-hello-dep2_dep2")
    set(FIPS_IMPORT)
endmacro()
if (FIPS_AUTO_IMPORT)
    fips_ide_group("Imports")
    fips_import_fips_hello_dep2_dep2()
    fips_ide_group("")
endif()
if (EXISTS "/Users/floh/projects/fips-hello-dep1/fips-include.cmake")
    include("/Users/floh/projects/fips-hello-dep1/fips-include.cmake")
endif()
if (EXISTS "/Users/floh/projects/fips-hello-dep1/lib/${FIPS_PLATFORM_NAME}")
    link_directories("/Users/floh/projects/fips-hello-dep1/lib/${FIPS_PLATFORM_NAME}")
endif()
include_directories("/Users/floh/projects/fips-hello-dep1/src")
macro(fips_import_fips_hello_dep1_dep1)
    set(FIPS_IMPORT 1)
    add_subdirectory("/Users/floh/projects/fips-hello-dep1/src/dep1" "fips-hello-dep1_dep1")
    set(FIPS_IMPORT)
endmacro()
if (FIPS_AUTO_IMPORT)
    fips_ide_group("Imports")
    fips_import_fips_hello_dep1_dep1()
    fips_ide_group("")
endif()
```


