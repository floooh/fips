fips
====

[![Build Status](https://travis-ci.org/floooh/fips.svg?branch=master)](https://travis-ci.org/floooh/fips)

fips is a highlevel build system wrapper written in Python for C/C++ projects.

Read the docs to get a better idea what this means:

http://floooh.github.io/fips/index.html

### Public Service Announcements

- **29-Jul-2015**: cross-compiling is now more flexible
    * cross-compile target platform names are no longer hardwired, fips projects can now add define their own cross-compile platforms
    * fips projects can now provide their own cmake-toolchain files or override the standard toolchain files

- **05-Feb-2015**: the NaCl SDK setup bug has been fixed by the NaCl team, so './fips setup nacl' should now work also with the latest Python 2.7.9

- **01-Feb-2015**: the code generation refactoring branch has been merged back into 
the master branch, code generation is now controlled with the new **fips_generate()**
cmake macro, see [Oryol engine](https://github.com/floooh/oryol) and 
[code generation doc page](http://floooh.github.io/fips/codegen.html) for details!

- **30-Jan-2015**: please note that the NaCl SDK setup script is currently broken with Python 2.7.9 (2.7.6 works), this is tracked in the following bug: https://code.google.com/p/chromium/issues/detail?id=452137  

### List of Fipsified Projects:

Libs and engines:

- **[accidentalnoise](https://code.google.com/p/accidental-noise-library/)**: https://github.com/mgerhardy/fips-accidentalnoise
- **[bgfx](https://github.com/bkaradzic/bgfx)**: https://github.com/floooh/fips-bgfx
- **[cjson](http://cjson.sourceforge.net/)**: https://github.com/floooh/fips-cjson
- **[cpptoml](https://github.com/skystrife/cpptoml)**: https://github.com/floooh/fips-cpptoml
- **[enet](https://github.com/lsalzman/enet)**: https://github.com/mgerhardy/fips-enet
- **[freetype2](http://git.savannah.gnu.org/cgit/freetype/freetype2.git/)**: https://github.com/mgerhardy/fips-freetype2
- **[glew](https://github.com/nigels-com/glew)**: https://github.com/fungos/fips-glew
- **[glfw](https://github.com/glfw/glfw)**: https://github.com/floooh/fips-glfw
- **[gliml](https://github.com/floooh/gliml)**: https://github.com/floooh/gliml
- **[glm](https://github.com/g-truc/glm)**: https://github.com/floooh/fips-glm
- **[googletest](https://code.google.com/p/googletest/)**: https://github.com/mgerhardy/fips-googletest
- **[imgui](https://github.com/ocornut/imgui)**: https://github.com/fungos/fips-imgui
- **[libcurl (precompiled)](http://curl.haxx.se/libcurl/)**: https://github.com/floooh/fips-libcurl
- **[libnoise](https://github.com/qknight/libnoise)**: https://github.com/mgerhardy/fips-libnoise
- **[nanovg](https://github.com/memononen/nanovg)**: https://github.com/fungos/fips-nanovg
- **[oryol](http://floooh.github.io/oryol/)**: https://github.com/floooh/oryol
- **[polyvox](https://bitbucket.org/volumesoffun/polyvox.git)**: https://github.com/mgerhardy/fips-polyvox
- **[recastnavigation](https://github.com/memononen/recastnavigation)**: https://github.com/fungos/fips-recast
- **[remotery](https://github.com/Celtoys/Remotery)**: https://github.com/floooh/fips-remotery
- **[sauce](https://github.com/phs/sauce)**: https://github.com/mgerhardy/fips-sauce
- **[simpleai](https://github.com/mgerhardy/simpleai)**: https://github.com/mgerhardy/fips-simpleai
- **[stb](https://github.com/nothings/stb)**: https://github.com/fungos/fips-stb
- **[turbobadger](https://github.com/fruxo/turbobadger)**: https://github.com/fungos/fips-turbobadger
- **[unittestpp](https://github.com/unittest-cpp/unittest-cpp)**: https://github.com/floooh/fips-unittestpp
- **[vld (precompiled)](https://github.com/KindDragon/vld)**: https://github.com/floooh/fips-vld
- **[zlib](http://www.zlib.net/)**: https://github.com/floooh/fips-zlib

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

