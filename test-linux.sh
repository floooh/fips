#!/bin/sh
git --version
python --version
# test fips command itself
python fips
# clone hello world project
python fips clone https://github.com/floooh/fips-hello-world.git
cd ../fips-hello-world
# test help command
python fips help
python fips help clone
python fips help config
python fips help open
python fips help setup
# test list command
python fips help list
python fips list
python fips list all
python fips list configs
python fips list build-tools
python fips list registry
python fips list settings
python fips list exports
python fips list imports
python fips list targets
# test diag command
python fips help diag
python fips diag
python fips diag all
python fips diag fips
python fips diag tools
python fips diag configs
python fips diag imports
# test fetch command
python fips help fetch
python fips fetch
python fips fetch fips-hello-dep2
# test gen command
python fips help gen
python fips gen
python fips gen linux-make-release
python fips list targets
# test build command
python fips help build
python fips build
python fips build linux-make-release
# test run command
python fips help run
python fips run hello
python fips run hello -- arg0 arg1 arg2
python fips run hello linux-make-release
python fips run hello linux-make-release -- arg0 arg1 arg2
# test clean command
python fips help clean
python fips clean
python fips clean linux-make-release
python fips clean all
# test set command
python fips help set
python fips set config linux-make-release
python fips set ccache on
# test make command
python fips make hello
python fips run hello
python fips make hello linux-make-debug
python fips run hello linux-make-debug
# test the update command
python fips update
# test unset command
python fips help unset
python fips unset config
python fips unset ccache
# test fips init command
python fips help init
mkdir ../test-project
python fips init test-project
# run imported commands
python fips help fips-hello-test
python fips fips-hello-test
python fips help fips-hello-dep1
python fips fips-hello-dep1
# test setting current target and num make jobs
python fips clean all
python fips set target hello
python fips set jobs 1
python fips set config linux-make-release
python fips list settings
python fips make
python fips run
python fips unset config
python fips unset target
python fips unset jobs
python fips list settings
# test shared lib (in fips-hello-dep1)
cd ../fips-hello-dep1
python fips gen
python fips build
# clone tests project
python fips clone https://github.com/fungos/fips-tests.git
cd ../fips-tests
python fips testrunner linux-make-debug
python fips testrunner linux-make-release

