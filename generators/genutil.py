"""Common utilities for generator scripts"""
import sys
import os
import platform

FilePath = ''
LineNumber = 0
Env = {}

#-------------------------------------------------------------------------------
def error(msg) :
    '''
    Just print a simple error message and return with error code 10.
    '''
    print("ERROR: {}".format(msg))
    sys.exit(10)

#-------------------------------------------------------------------------------
def setErrorLocation(filePath, lineNumber) :
    global FilePath
    global LineNumber
    FilePath = filePath
    LineNumber = lineNumber

#-------------------------------------------------------------------------------
def fmtError(msg, terminate=True) :
    '''
    Print an error message formatted so that IDEs can parse them,
    and return with error code 10.
    '''
    if platform.system() == 'Windows' :
        print('{}({}): error: {}'.format(FilePath, LineNumber + 1, msg))
    else :
        print('{}:{}:0: error: {}\n'.format(FilePath, LineNumber + 1, msg))
    if terminate:
        sys.exit(10)

#-------------------------------------------------------------------------------
def fmtWarning(msg) :
    '''
    Print an warning message formatted so that IDEs can parse them.
    '''
    if platform.system() == 'Windows' :
        print('{}({}): warning: {}'.format(FilePath, LineNumber + 1, msg))
    else :
        print('{}:{}:0: warning: {}\n'.format(FilePath, LineNumber + 1, msg))

#-------------------------------------------------------------------------------
def fileVersionDirty(filePath, version) :
    '''
    Reads the first 4 lines of a file, checks whether there's an 
    $$version:X statemenet in it, returns False if the version
    number in the file is equal to the arg version.
    '''
    f = open(filePath, 'r')
    for i in range(0,4) :
        line = f.readline()
        startIndex = line.find('#version:')
        if startIndex != -1 :
            endIndex = line.find('#', startIndex + 9)
            if endIndex != -1 :
                versionNumber = line[startIndex + 9 : endIndex]
                if int(versionNumber) == version :
                    return False

    # fallthrough: no version or version doesn't match
    return True

#-------------------------------------------------------------------------------
def isDirty(version, inputs, outputs) :
    '''
    Check if code generation needs to run by comparing version stamp
    and time stamps of a number of source files, and generated
    source and header files.

    :param version:     generator version number, or None
    :param input:       a list of absolute input file paths
    :param outputs:     a list of absolute output file paths
    :returns:           True if at least one output file is 'dirty'
    '''
    for output in outputs :
        if not os.path.exists(output):
            return True
        if version :
            if fileVersionDirty(output, version) :
                return True
        outputTime = os.path.getmtime(output)
        for input in inputs :
            inputTime = os.path.getmtime(input)
            if inputTime > outputTime :
                return True
    return False

#-------------------------------------------------------------------------------
def setEnv(dic) :
    '''
    Set the 'environemnt' (key/value pairs accessible by getEnv(key)
    '''
    global Env
    Env = dic

#-------------------------------------------------------------------------------
def getEnv(key) :
    '''
    Return an 'environment variable' value.
    '''
    global Env
    return Env[key]

