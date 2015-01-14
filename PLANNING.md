
#### Workspace:

- a directory with several **projects**
- exactly one **fips** directory
- 2 ways to setup fips:
    - git clone fips into workspace manually
    - or: git clone project, and run "fips bootstrap" from there
    
```
workspace/
    project1/
        fips.yml
    project2/
        fips.yml
    project3/
        fips.yml
    fips/
```

#### Project:
- a collection of related Modules, ExtLibs and/or Apps
- in one directory
- in one git repo
- with a unique short name associated with a git URL
- with one fips.yml file in the root directory 
- with one root CMakeLists.txt file which builds the project
- can have dependencies into external projects

#### Module:
- a collection of related sources compiling into a static link lib
- lives in a Project
- can depend on other Modules and ExtLibs either in the local project or external projects
- with one CMakeLists
- modules must have a 'namespaced name', namespace is their project

#### ExtLib:
- a 'raw' module of sources compiling into a static link lib
- cannot depend on other Modules or ExtLibs
- more freedom in CMakeLists
- can contain of header + precompiled static libs (doesn't have to be compiled)
- usually used to integrate 3rd party libs
- lives in a project
- ExtLibs must have a 'namespaced name', namespace is their  project

#### App:
- an application/executable
- can depend on Modules and ExtLibs, local or external ones
- lives in a project

#### fips.yml
- one per project in the root directory
- lists all modules, extlibs and apps in the project
- contains meta data (author, license, description, ...)
- contains project specific attributes (supported platforms, ...)
- most importantly lists external dependencies (modules and extlibs)
- can define aliases to override dependencies (for instance for 
  replacing standard modules with custom ones)
- can define aliases for toolchain files to override the standard
  cmake platform defines
- QUESTION: what stuff lives in the fips.yml and what lives in CMakeLists.txt?

#### fips:
- 'main control script'
- fips [verb] [noun] [attrs]
- usually executed from a small imposter script from within a project root

      

 
