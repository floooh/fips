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

### TODO:

Writing Generators:

* dirty check
* modification time
* version stamp

Under the hood:

* the fips_generate.yml file
...

