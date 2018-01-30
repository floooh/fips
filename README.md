fips
====

[![Build Status](https://travis-ci.org/floooh/fips.svg?branch=master)](https://travis-ci.org/floooh/fips)

fips is a highlevel build system wrapper written in Python for C/C++ projects.

Read the docs to get a better idea what this means:

http://floooh.github.io/fips/index.html

### Public Service Announcements

- **30-Jan-2018**: Android support has been modernized, usage should
be the same as before, but there are some nice changes under the hood:
  - ```fips setup android``` now only downloads the SDK Tools archive,
  and uses the contained ```sdkmanager``` tool to install the required
  SDK components (including the NDK)
  - fips is now using the official Android NDK cmake toolchain file
  - Android builds no longer require the ```ant``` tool, and also
  don't need Gradle or Android Studio to build projects, instead
  APKs are created directly created from a small python helper script
  called from a cmake post-build job
  - you can now use Android Studio for debugging (tested so far on 
  Mac and Linux), select the ```Profile or debug APK``` option when
  starting Android Studio, and follow the steps (sometimes debugging
  still seems to hang or ignore breakpoints on first start, in this
  case, just stop debugging and try again)
  - some things are not yet configurable:
    - can't yet override the default AndroidManifest.xml
    - can't yet sign APKs with your own key
    - can't yet add Java code to the APK

- **16-Jan-2018**: The iOS build configs now put the resulting .app bundle
into the ```fips-deploy/[proj]/[config]/``` directory, so they behave
the same as most other target platforms. This makes it
easier for helper scripts (code generators and verbs) to
find the iOS app bundle (for instance to copy asset files).

- **05-Jan-2018**: Import definitions in fips.yml files can now contain an
expression which is evaluated in cmake. This can be used to include or
exclude platform-specific includes. [See here for details](http://floooh.github.io/fips/imports.html)

- **04-Jan-2018**: The previously experimental Visual Studio Code support is
now 'official', [see here for details](http://floooh.github.io/2018/01/04/vscode-fips.html)

- **16-Aug-2017**: I found (and fixed) some inconsistent behaviour when 
the cmake project name is different from the project's directory name,
this may change the behaviour of cmake- and python-code-generator
scripts which used the FIPS\_PROJECT\_DEPLOY\_DIR and 
FIPS\_PROJECT\_BUILD\_DIR (but the previous behaviour was clearly a bug,
which only manifested itself if the cmake project name and directory
name differed). See this ticket for details: https://github.com/floooh/fips/issues/154

- **25-Apr-2017**: I committed a small fix which changes the order of
imported dependencies so that imported dependencies now always come
before the importing project. This was often also the case previously
but could fail in cases where the same dependency was included from
different projects. No changes should be required in your project,
at least if the dependency tree was defined correctly and didn't
depend on some hidden ordering.

- **27-Mar-2017**: the root path of the emscripten SDK has changed from
emsdk\_portable to emsdk-portable, a fix has been committed, but you
need to setup the emscripten SDK again (first, wipe the fips-sdks directory,
then run './fips setup emscripten' again from a project directory)

- **25-Feb-2017**: what happened in the last year:
  - python3 compatibility contributed by Levente Polyak (thanks!)
  - various Eclipse fixes contributed by Martin Gerhardy (thanks!)
  - Windows: Cygwin support contributed by Fungos, many thanks! also 
    for the many smaller fixes :)
  - new verb './fips update' updates all dependencies (unless
    they have uncommitted or unpushed changes)
  - new helper functions git.add, git.commit and git.push,
    these are not exposed as fips verbs, but are useful
    for writing your own verbs (e.g. build automation scripts)
  - emscripten: removed the FIPS\_EMSCRIPTEN\_EXPORTED\_FUNCTIONS
    cmake options, this is better done by directly annotating
    exported functions with EMSCRIPTEN_KEEPALIVE (or soon
    [EMSCRIPTEN_EXPORT](https://github.com/kripken/emscripten/pull/4977))
  - a new predefined cmake variable FIPS\_BUILD\_DIR, this points
    to the build root directory (../fips\_build)
  - two new predefined cmake variables FIPS\_PROJECT\_BUILD\_DIR
    and FIPS\_PROJECT\_DEPLOY\_DIR, these are useful to pass
    as arguments to code generator scripts
  - emscripten: use linker response files when using the UNIX
    Makefiles generator to workaround command line length limit 
    on Windows
  - emscripten: on Windows, use the the Emscripten SDK incoming
    branch (requires LLVM compilation, but behaviour is now the
    same as on OSX and Linux)
  - fips\_files\_ex() and related cmake functions now warn if 
    the globbed file list is empty, previously this generated
    a rather cryptic cmake syntax error message
  - emscripten: added support for WebAssembly (toolchain flags 
    and build configs)
  - emscripten: added a config option FIPS\_EMSCRIPTEN\_USE\_WEBGL2
  - emscripten: added new cmake options 
    FIPS\_EMSCRIPTEN\_USE\_CPU\_PROFILER and 
    FIPS\_EMSCRIPTEN\_USE\_MEMORY\_PROFILER (these generate a build
    with emscripten's built-in cpu and memory profilers)
  - emscripten: added a FIPS\_EMSCRIPTEN\_USE\_SAFE\_HEAP cmake option
  - emscripten: use the smaller 'shell\_minimal.html' file instead
    of the original file which has a big SVG logo in it
  - emscripten: use the -s NO\_EXIT\_RUNTIME which slightly 
    reduces code size 
  - Windows UWP support (not in daily use though)

- **26-Feb-2016**: cmake generator definition in fips build config files
is now more flexible by exposing the cmake -A (generator platform) 
and -T options (generator toolset), there's now also a 'Default' generator
which lets cmake select the 'best' build file generator for the platform. All this
together simplifies the version situation with Visual Studio on Windows. 
Previously, the build config win64-vs2013-debug was used as default config.
When only VS2015 is installed, generating build files had failed, unless
the build config win64-vs2015-debug was selected manually. Now there's
a new generic default config called **win64-vstudio-debug**. This lets
cmake pick whatever VStudio version is installed. Of course it is still
possible to pick a specific Visual Studio version with the 'old' build
configs \*-vs2013-\* and \*-vs2015-\*.

- **14-Feb-2016**: fips can now import dependencies pinned to a specific git
  revision (previously only by tag or branch name). Many thanks to fungos
  (https://github.com/fungos) for implementing this! Here's how a specific
  revision is specified in the fips.yml file:
```
  imports:
    fips-hello-dep3:
      git:    https://github.com/fungos/fips-hello-dep3.git
      rev:    191f59f0
```
- **03-Dec-2015**: I have added a new 'no\_auto\_import' policy/feature for
  advanced uses which allows to manually select modules from imported 
  projects. This is more work but can provide a cleaner project layout
  if only a few modules from imported projects are needed. See the
  documentation web page for details (http://floooh.github.io/fips/imports.html, 
  search for 'Selectively importing modules'). The default behaviour should
  be exactly as before. If anything is broken in your project, please
  don't hesitate to write a ticket :)

- **13-Oct-2015**: 'fips run' has learned to run Android apps, after building
  your project with one of the Android build configs, simply do a 
  'fips run [target]' like on the other platforms. This will (re-)install
  the app, launch it, and then run 'adb logcat' (simply hit Ctrl-C when done)

- **10-Oct-2015**: I committed a simplification for nested dependency
  resolution yesterday (turns out cmake does this on its own with
  'target_link_libraries'), however this may introduce some link-order problems
  in existing projects when using GCC or emscripten. If your project no longer
  links because of this, and you think that fixing the depedency order in the
  CMakeLists.txt files is too big a hassle and fips should take care of this,
  please simply open a ticket, and I'll try to find a solution in fips. I
  haven't made up my mind about this either yet, the few cases in Oryol were
  easy to fix, but larger projects may be more tricky to fix.

- **29-Jul-2015**: cross-compiling is now more flexible
    * cross-compile target platform names are no longer hardwired, fips
      projects can now add define their own cross-compile platforms
    * fips projects can now provide their own cmake-toolchain files or override
      the standard toolchain files

- **05-Feb-2015**: the NaCl SDK setup bug has been fixed by the NaCl team, so
  './fips setup nacl' should now work also with the latest Python 2.7.9

- **01-Feb-2015**: the code generation refactoring branch has been merged back
  into the master branch, code generation is now controlled with the new
  **fips_generate()** cmake macro, see [Oryol
  engine](https://github.com/floooh/oryol) and [code generation doc
  page](http://floooh.github.io/fips/codegen.html) for details!

- **30-Jan-2015**: please note that the NaCl SDK setup script is currently
  broken with Python 2.7.9 (2.7.6 works), this is tracked in the following bug:
  https://code.google.com/p/chromium/issues/detail?id=452137  

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
- **[nativefiledialog](https://github.com/mlabbe/nativefiledialog)**: https://github.com/fungos/fips-nfd
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

