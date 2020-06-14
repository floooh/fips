---
title: "Code Generation"
weight: 8
# bookFlatSection: false
# bookShowToC: true
---
# Code Generation

Fips makes it easy to generate C/C++ source code by running Python scripts
during the build process. Special care has been taken to make code generation flexible so
that it is useful for many different scenarios. For instance here are
a few examples how the Oryol 3D engine uses code generation:

* generate code for serializable message protocols (similar to [Google protobuf](https://code.google.com/p/protobuf/))
* embed image files into header files and generate a sprite sheet library
* GLSL shader editing with IDE error integration (see [this blog post](http://flohofwoe.blogspot.de/2014/05/shader-compilation-and-ides.html) and [video](http://www.youtube.com/watch?v=Up9LFP5DMvw))

### Using Code Generation

The **fips_generate** cmake macro is used to tell fips how to generate C/C++ source code:

```cmake
fips_generate(FROM input_file
              [TYPE generator_type]
              [SRC_EXT source_file_extension]
              [HDR_EXT header_file_extension]
              [SOURCE out_source_file]
              [HEADER out_header_file]
              [ARGS args_as_yaml_string])
```

Where:

* **FROM**: Defines an input data file which is handed to the Python generator script
as argument, the input file can be anything, for instance JSON, YAML, XML or GLSL. It is
up to the generator script to make sense of the input file.
* **TYPE**: Defines the generator that should be used for code generation, this resolves
to a Python module which is imported and run at build time
* **SOURCE**: The filename of the generated source code file
* **HEADER**: The filename of the generated header code file
* **SRC_EXT**: Optional file extension for the generated source file (default is ".cc")
* **HDR_EXT**: Optional file extension for the generated header file (default is ".h")
* **ARGS**: An optional YAML formatted string defining additional arguments to the python
generator script.

> NOTE that SRC_EXT and HDR_EXT are ignored if SOURCE and/or HEADER is also defined

Let's go through a few examples:

The most usual form to call fips_generate() is to provide only a FROM and TYPE
argument:

```cmake
fips_generate(FROM IOProtocol.yml TYPE MessageProtocol)
```

This means that the input file _IOProtocol.yml_ is converted by the generator
_MessageProtocol_ into the output files _IOProtocol.cc_ and _IOProtocol.h_.

If both the _SOURCE_ and _HEADER_ args are **not** provided, fips will
automatically generate one _.cc_ source and one _.h_ header file with the same base
name as the _FROM_ file.

To generate output files with different file extensions, provide _SRC\_EXT_
and/or _HDR\_EXT_:

```cmake
fips_generate(FROM IOProtocol.yml TYPE MessageProtocol SRC_EXT ".cpp" HDR_EXT ".hpp")
```

To generate output files with different filenames, provide them explicitly with
the _SOURCE_ and _HEADER_ args, in this case _SRC\_EXT_ and _HDR\_EXT_ are
ignored:

```cmake
fips_generate(FROM IOProtocol.yml
              TYPE MessageProtocol
              SOURCE IOProtocol_Generated.cpp
              HEADER IOProtocol_Generated.hpp)
```

Providing only **one** of _SOURCE_ or _HEADER_ means that the generator
should only generate either a source file or a header file, but not both.
This only works if the generator script knows that it should only write
one source or one header file.

The following example generates only a source file, but no header:

```cmake
fips_generate(FROM MyFile.xml TYPE MySourceGenerator SOURCE MyFile.cc)
```

Likewise, this example only generates a header, but no source:

```cmake
fips_generate(FROM MyFile.xml TYPE MyHeaderGenerator HEADER MyFile.h)
```

If the _TYPE_ argument is omitted, the _FROM_ argument must be
a Python file in the project source tree which is directly called to
create the output source files:

```cmake
fips_generate(FROM spritesheet.py)
```

In this case, the Python script _spritesheet.py_ in the current
source code location will be called to generate the files
_spritesheet.cc_ and _spritesheet.h_.

It is possible to provide additional arguments to the generator script
in a YAML-formatted string:

```cmake
fips_generate(FROM fs_metaballs.sc
              TYPE BgfxShaderEmbedded
              HEADER fs_metaballs.bin.h
              ARGS "{ type: fs, bla: blub }")
```

### Writing Generators

A _generator_ is a Python script which is called to generate C/C++ files.

Fips doesn't come with its own generators, instead it looks in the
**fips-files/generators** directory in the current project and imported projects
for generator scripts.

Let's check what generators Oryol has to offer:

```
> cd oryol/fips-files/generators
> ls *.py
MessageProtocol.py Shader.py          SoundSheet.py      SpriteSheet.py
```

A generator script must contain a Python function called 'generate()',
which can have the following forms (with or without args):

```python
# this is called if fips_generate() didn't have an ARGS argument:
def generate(input, out_src, out_hdr) :
    ...

# this is called if fips_generate() was called with ARGS:
def generate(input, out_src, out_hdr, args) :
    ...
```

Where:

* **input**: is the absolute path to the input file (provided with the _FROM_ cmake
argument of fips_generate())
* **out_src**: is the absolute path to the output source file, or None (provided with the
_SOURCE_ cmake argument to fips_generate())
* **out_hdr**: is the absolute path to the output header file, or None (provided with the
_HEADER_ cmake argument to fips_generate())
* **args**: if present, this is a dictionary of key/value pairs defined in the
_ARGS_ cmake argument to fips_generate()

### Target Platform Detection

Sometimes you'll need to do things differently when cross-compiling to
specific target platforms. Use the _getutil.getEnv()_ method with the
key _target\_platform_ to check the target platform, for instance to check
for iOS:

```python
import genutil

def only_on_ios():
    if genutil.getEnv('target_platform') == 'ios':
        # building for iOS...
```

The valid target platform names are the same as in the cmake variable
_FIPS\_PLATFORM\_NAME_:

- ios
- osx
- android
- linux
- linuxraspbian
- win64
- win32

### File Dirty Check

Generator scripts should not overwrite the target files if nothing has changed
in the source file, otherwise they would trigger unnecessary recompiles higher
up the source code dependency chain.

fips provides a simple helper function to perform 2 types of dirty checks:

- check the file modification timestamps of input files against the
modification timestamps of the generated source code files
- check a _generator version_ embedded in the first few lines of generated
files

The second _generator version_ check seems unusual, but this is very useful
when the generator scripts themselves are updated. For every change in
a generator script that influences the generated source code, the generator's
version number should be incremented. On the next build, all files generated
by this generator script will be written because the generator version
number doesn't match.

Let's have a look at a very simple generator script:

```python
"""fips imported code generator for testing"""

Version = 2

import genutil as util

#-------------------------------------------------------------------------------
def generateHeader(hdrPath) :
    with open(hdrPath, 'w') as f :
        f.write("// #version:{}#\n".format(Version))
        f.write("extern void test_func(void);\n")

#-------------------------------------------------------------------------------
def generateSource(srcPath) :
    with open(srcPath, 'w') as f :
        f.write("// #version:{}#\n".format(Version))
        f.write("#include <stdio.h>\n")
        f.write("void test_func() {{\n")
        f.write('    printf("Hello from test_func!\\n");\n')
        f.write('}\n')

#-------------------------------------------------------------------------------
def generate(input, out_src, out_hdr) :
    if util.isDirty(Version, [input], [out_src, out_hdr]) :
        generateHeader(out_hdr)
        generateSource(out_src)
```

Note the **Version = 2** statement in line 3, this is the 'generator version',
bumping this number will mark all generated source files as dirty and cause
all generated files to be overwritten regardless of their file modification time stamp.

The generator entry point is the **generate()** function in line 23, the first
line of this function checks whether the generator needs to run, first by checking
the version stamp, then by checking the file modification times of the input
file(s) and output files.

Header and source file are then written by the **generateHeader()** and
**generateSource()** functions.

Note that both functions write a magic version tag inside a C comment in the first
line which looks like **#version:2#**. The **isDirty()** helper function will
look in the first 4 text lines for this magic tag.

> NOTE: it is possible to provide 'None' as version argument to genutil.isDirty(),
in this case, no version check will be performed

The generated source files will look like this, first the header:

```c
// #version:2#
extern void test_func(void);
```

...and the source file:

```c
// #version:2#
#include <stdio.h>
void test_func() {
    printf("Hello from test_func!\n");
}
```

The generator in this example doesn't actually use an input file since
it generates the target files without any parameterization. This very special
case only works with a Python script in the source tree which serves as
'input file' and calls the above generator 'hello_generator':

```python
import hello_generator as gen

def generate(input, out_src, out_hdr) :
    gen.generate(input, out_src, out_hdr)
```

The final missing piece is the CMakeLists.txt entry:

```cmake
fips_begin_module(dep2)
    fips_generate(FROM hello.py)
fips_end_module()
```

### Under the hood

This is what happens under the hood for code generation:

**in './fips gen'**:

A python file '.fips-gen.py' is created in the project root directory.
This sets up the python module search path to all imported projects so that
imported code-generator scripts can be found, and will be called during
the build process to load and invoke the code generator scripts.

**in fips_generate()**:

- absolute filesystem paths for the FROM, SOURCE and HEADER files are derived
- generate empty SOURCE and HEADER files in the same directory as the FROM
file, if they don't exist yet (this is a cmake requirement, all source code
files added to a build target must exist)
- add the FROM, SOURCE and HEADER files to the current build target's file list
- a YAML file will be populated with the information from all fips\_generate()
calls at ${CMAKE\_BINARY\_DIR}/fips\_codegen.yml (which is at
./fips-build/[proj-name]/[config-name]/fips\_codegen.yml)
- set a global flag that the current project has code generation

**in fips\_end\_xxx()**:

- the global 'project has code generation' flag is set, generate a cmake
custom target named _ALL\_GENERATE_ which calls the generated '.fips-gen.py' script
with the also generated fips_codegen.yml file as argument
- add the ALL\_GENERATE custom build target as dependency to all build targets
with code generation

**during builds**:

- ALL\_GENERATE custom build target will run before any regular build target
which depends on generated code
- the ALL\_GENERATE target runs the python file '.fips-gen.py' from the
project root directory with the fips\_codegen.yml file as argument
- '.fips-gen.py' loads the fips\_codegen.yml file, and imports and runs
code generator python scripts, which will generate the C/C++ source code files
as needed



