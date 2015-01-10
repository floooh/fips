---
layout: page
title: About Fips
permalink: index.html
---

TODO!

Highlighting tests:

{% highlight bash %}
> cd bla
> ./fips blub
{% endhighlight %}

{% highlight yaml %}
---
platform: emscripten 
generator: Unix Makefiles
build_tool: make
build_type: Debug
{% endhighlight %}

{% highlight cmake %}
cmake_minimum_required(VERSION 2.8)

# include the fips main cmake file
get_filename_component(FIPS_ROOT_DIR "../fips" ABSOLUTE)
include("$${FIPS_ROOT_DIR}/cmake/fips.cmake")

# include_directories(src)

fips_setup()
fips_project($project)
# fips_add_subdirectory(src/...)
# fips_add_subdirectory(src/...)
fips_finish()
{% endhighlight %}

