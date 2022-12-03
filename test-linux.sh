#!/bin/sh
git --version
python3 --version
# test fips command itself
python3 fips
# clone hello world project
python3 fips clone https://github.com/floooh/fips-hello-world.git
cd ../fips-hello-world
# test help command
python3 fips help
python3 fips help clone
python3 fips help config
python3 fips help open
python3 fips help setup
# test list command
python3 fips help list
python3 fips list
python3 fips list all
python3 fips list configs
python3 fips list build-tools
python3 fips list registry
python3 fips list settings
python3 fips list exports
python3 fips list imports
python3 fips list targets
# test diag command
python3 fips help diag
python3 fips diag
python3 fips diag all
python3 fips diag fips
python3 fips diag tools
python3 fips diag configs
python3 fips diag imports
# test fetch command
python3 fips help fetch
python3 fips fetch
python3 fips fetch fips-hello-dep2
# test gen command
python3 fips help gen
python3 fips gen
python3 fips gen linux-make-release
python3 fips list targets
# test build command
python3 fips help build
python3 fips build
python3 fips build linux-make-release
# test run command
python3 fips help run
python3 fips run hello
python3 fips run hello -- arg0 arg1 arg2
python3 fips run hello linux-make-release
python3 fips run hello linux-make-release -- arg0 arg1 arg2
# test clean command
python3 fips help clean
python3 fips clean
python3 fips clean linux-make-release
python3 fips clean all
# test set command
python3 fips help set
python3 fips set config linux-make-release
# test make command
python3 fips make hello
python3 fips run hello
python3 fips make hello linux-make-debug
python3 fips run hello linux-make-debug
# test the update command
python3 fips update
# test unset command
python3 fips help unset
python3 fips unset config
# test fips init command
python3 fips help init
mkdir ../test-project
python3 fips init test-project
# run imported commands
python3 fips help fips-hello-test
python3 fips fips-hello-test
python3 fips help fips-hello-dep1
python3 fips fips-hello-dep1
# test setting current target and num make jobs
python3 fips clean all
python3 fips set target hello
python3 fips set jobs 1
python3 fips set config linux-make-release
python3 fips list settings
python3 fips make
python3 fips run
python3 fips unset config
python3 fips unset target
python3 fips unset jobs
python3 fips list settings
# test shared lib (in fips-hello-dep1)
cd ../fips-hello-dep1
python3 fips gen
python3 fips build
# clone tests project
python3 fips clone https://github.com/fips-libs/fips-tests.git
cd ../fips-tests
python3 fips testrunner linux-make-debug
python3 fips testrunner linux-make-release
