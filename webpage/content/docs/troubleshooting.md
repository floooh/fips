---
title: "Troubleshooting"
weight: 3
# bookFlatSection: false
# bookShowToC: true
---

# Troubleshooting

If anything goes wrong, './fips clean all' and './fips diag' are the two
most useful commands.

'./fips clean all' deletes all build files created by fips and thus
resets a project into a clean starting state.

'./fips diag' runs a number of diagnostic tests and provides useful
error output:

```
> ./fips help diag
fips diag
fips diag all
fips diag fips
fips diag tools
fips diag configs
fips diag imports
    run diagnostics and check for errors
> _
```

'./fips diag tools' tests whether additional 3rd party tools are present, 
and if not found, explains whether the tools are required or optional,
and what they are needed for.

```
> ./fips diag tools
=== tools:
git:	found
cmake:	found
ccmake:	found
make:	found
ninja:	OPTIONAL, NOT FOUND (required for building '*-ninja-*' configs)
xcodebuild:	found
java:	found
ant:	found
python2:	found
> _
```

'./fips diag fips' simply checks whether fips itself is up-to-date. If 
not, simply run a 'git pull' from within the fips directory to get the
latest version.

```
=== fips:
  uptodate
```

'./fips diag configs' goes through all existing build config files, checks
if their content is valid, and whether all required prerequisites are met
in the current environment to build them (e.g. whether the required build
tools exist and cross-platform SDKs have been installed):

```
> ./fips diag configs
=== configs:
...
ios-xcode-debug
  ok
ios-xcode-release
  ok
linux-make-debug
  'linux' is not a valid target platform for host 'osx'
linux-make-release
  'linux' is not a valid target platform for host 'osx'
...
> _
```
