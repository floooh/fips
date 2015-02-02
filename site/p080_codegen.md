---
layout: page
title: Code Generation 
permalink: codegen.html
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

{% highlight cmake %}
fips_generate(FROM input_file
              [TYPE generator_type]
              [SOURCE out_source_file]
              [HEADER out_header_file])
{% endhighlight %}


Where:

* **FROM**: Defines an input data file which is handed to the Python generator script 
as argument, the input file can be anything, for instance JSON, YAML, XML or GLSL. It is 
up to the generator script to make sense of the input file.
* **TYPE**: Defines the generator that should be used for code generation, this resolves
to a Python module which is imported and run at build time
* **SOURCE**: The filename of the generated source code file
* **HEADER**: The filename of the generated header code file

Let's go through a few examples:

The most usual form to call fips_generate() is to provide only a FROM and TYPE
argument:

{% highlight cmake %}
fips_generate(FROM IOProtocol.yml TYPE MessageProtocol)
{% endhighlight %}

This means that the input file _IOProtocol.yml_ is converted by the generator
_MessageProtocol_ into the output files _IOProtocol.cc_ and _IOProtocol.h_.

If both the _SOURCE_ and _HEADER_ args are **not** provided, fips will
automatically generate one _.cc_ source and one _.h_ header file with the same base 
name as the _FROM_ file.

To generate output files with different file extensions (or filenames), provide
them explicitely with the _SOURCE_ and _HEADER_ args, e.g.:

{% highlight cmake %}
fips_generate(FROM IOProtocol.yml
              TYPE MessageProtocol
              SOURCE IOProtocol.cpp
              HEADER IOProtocol.hh)
{% endhighlight %}

Providing only **one** of _SOURCE_ or _HEADER_ means that the generator
should only generate either a source file or a header file, but not both.
This only works if the generator script knows that it should only write
one source or one header file.

The following example generates only a source file, but no header:

{% highlight cmake %}
fips_generate(FROM MyFile.xml TYPE MySourceGenerator SOURCE MyFile.cc)
{% endhighlight %}

Likewise, this example only generates a header, but no source:

{% highlight cmake %}
fips_generate(FROM MyFile.xml TYPE MyHeaderGenerator HEADER MyFile.h)
{% endhighlight %}

If the _TYPE_ argument is omitted, the _FROM_ argument must be
a Python file in the project source tree which is directly called to
create the output source files:

{% highlight cmake %}
fips_generate(FROM spritesheet.py)
{% endhighlight %}

In this case, the Python script _spritesheet.py_ in the current
source code location will be called to generate the files
_spritesheet.cc_ and _spritesheet.h_.

### Writing Generators

A _generator_ is a Python script which is called to generate C/C++ files.

Fips doesn't come with its own generators, instead it looks in the 
**fips-generators** directory in the current project and imported projects
for generator scripts.

Let's check what generators Oryol has to offer:

{% highlight bash %}
> cd oryol/fips-generators
> ls *.py
MessageProtocol.py Shader.py          SoundSheet.py      SpriteSheet.py
{% endhighlight %}

A generator script must contain a Python function called 'generate()':

{% highlight python %}
def generate(input, out_src, out_hdr) :
    ...
{% endhighlight %}

Where:

* **input**: is the absolute path to the input file (provided with the _FROM_ cmake 
argument of fips_generate())
* **out_src**: is the absolute path to the output source file, or None (provided with the
_SOURCE_ cmake argument to fips_generate())
* **out_hdr**: is the absolute path to the output header file, or None (provided with the
_HEADER_ cmake argument to fips_generate())

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
version number should be increment. On the next build, all files generated
by this generator script will be written because the generator version
number doesn't match.

Let's have a look at a very simple generator script:

{% highlight python linenos %}
{% raw %}
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

{% endraw %}
{% endhighlight %}

Note the **Version = 2** statement in line 3, this is the 'generator version',
bumping this number will mark all generated source files as dirty and cause
all generated files to be overwritten regardless of their file modification time stamp.

The generator entry point is the **generate()** function in line 23, the first
line of this function checks whether the generator needs to run, first by checking
the version stamp, then by checking the file modification times of the input
file(s) and output files.

Header and source file are then written by the **generateHeader()** and
**generateSource()** functions.

Note that both functions write a comment in the first line a magic version
tag which looks like **#version:2#**. The **isDirty()** helper function will
look in the first 4 text lines for this magic tag.

The generated source files will look like this, first the header:

{% highlight c %}
{% raw %}
// #version:2#
extern void test_func(void);
{% endraw %}
{% endhighlight %}

...and the source file:

{% highlight c %}
{% raw %}
// #version:2#
#include <stdio.h>
void test_func() {
    printf("Hello from test_func!\n");
}
{% endraw %}
{% endhighlight %}

The generator in this example doesn't actually use an input file since
it generates the target files without any parameterization. This very special
case only works with a Python script in the source tree which serves as 
'input file' and calls the above generator 'hello_generator':

{% highlight python %}
import hello_generator as gen

def generate(input, out_src, out_hdr) :
    gen.generate(input, out_src, out_hdr)
{% endhighlight %}

The final missing piece is the CMakeLists.txt entry:

{% highlight cmake %}
fips_begin_module(dep2)
    fips_generate(FROM hello.py)
fips_end_module()
{% endhighlight %}

### Under the hood

TODO! (fips_generate.yml, .fips-gen.py)

