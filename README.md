fips
====

[![Build Status](https://travis-ci.org/floooh/fips.svg?branch=master)](https://travis-ci.org/floooh/fips)

fips is a highlevel build system wrapper written in Python for C/C++ projects.

Read the docs to get a better idea what this means:

http://floooh.github.io/fips/index.html

### Public Service Announcements

- **05-Feb-2015**: the NaCl SDK setup bug has been fixed by the NaCl team, so './fips setup nacl' should now work also with the latest Python 2.7.9

- **01-Feb-2015**: the code generation refactoring branch has been merged back into 
the master branch, code generation is now controlled with the new **fips_generate()**
cmake macro, see [Oryol engine](https://github.com/floooh/oryol) and 
[code generation doc page](http://floooh.github.io/fips/codegen.html) for details!

- **30-Jan-2015**: please note that the NaCl SDK setup script is currently broken with Python 2.7.9 (2.7.6 works), this is tracked in the following bug: https://code.google.com/p/chromium/issues/detail?id=452137  

### List of Fipsified Projects:

In no particular order (this list may not always be uptodate,
check the registry.yml file for the latest additions, also
there may be fipsified projects that are not in the registry):

- **oryol**:                https://github.com/floooh/oryol.git
- **gliml**:                https://github.com/floooh/gliml.git
- **fips-glm**:             https://github.com/floooh/fips-glm.git
- **fips-unittestpp**:      https://github.com/floooh/fips-unittestpp.git
- **fips-zlib**:            https://github.com/floooh/fips-zlib.git
- **fips-glfw**:            https://github.com/floooh/fips-glfw.git
- **fips-libcurl**:         https://github.com/floooh/fips-libcurl.git
- **fips-polyvox**:         https://github.com/mgerhardy/fips-polyvox.git
- **fips-simpleai**:        https://github.com/mgerhardy/fips-simpleai.git
- **fips-bgfx**:            https://github.com/floooh/fips-bgfx.git
- **fips-remotery**:        https://github.com/floooh/fips-remotery.git
- **fips-accidentalnoise**: https://github.com/mgerhardy/fips-accidentalnoise.git
- **fips-enet**:            https://github.com/mgerhardy/fips-enet.git
- **fips-vld**:             https://github.com/floooh/fips-vld.git
- **fips-cjson**:           https://github.com/floooh/fips-cjson.git
- **fips-sauce**:           https://github.com/mgerhardy/fips-sauce
- **fips-googletest**:      https://github.com/mgerhardy/fips-googletest
- **fips-freetype2**:       https://github.com/mgerhardy/fips-freetype2

Test projects:

- **oryol-test-app**:     https://github.com/floooh/oryol-test-app.git
- **fips-hello-world**:   https://github.com/floooh/fips-hello-world.git
- **fips-hello-dep1**:    https://github.com/floooh/fips-hello-dep1.git
- **fips-hello-dep2**:    https://github.com/floooh/fips-hello-dep2.git

### Progress

fips is currently heavily **work in progress**, everything may change or
break at any time.

I'm trying to put up progress videos from time to time:

- first progress video: https://www.youtube.com/watch?v=6F_AecDqRIY
- 2nd progress video: https://www.youtube.com/watch?v=W0MYjpR0G8c
- 3rd progress video: https://www.youtube.com/watch?v=3bQrYYaYU4w
- 4th progress video: https://vimeo.com/115050871
- using fips with Oryol 3D engine: https://www.youtube.com/watch?v=LaC4Sqatyts
- compiling and debugging in QtCreator and CLion IDEs: https://www.youtube.com/watch?v=Sp5TywYeNzE
- building a standalone Oryol app: https://www.youtube.com/watch?v=z8nwrGh2Zsc

