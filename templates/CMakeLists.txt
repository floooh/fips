#
# project: $project
#
cmake_minimum_required(VERSION 3.21)
project($project)
# include the fips main cmake file
get_filename_component(FIPS_ROOT_DIR "../fips" ABSOLUTE)
include("$${FIPS_ROOT_DIR}/cmake/fips.cmake")

# include_directories(src)
fips_setup()
# add_subdirectory(src/...)
# add_subdirectory(src/...)
