'''
    run diagnosis
'''

import platform
from tools import cmake,ccmake,cmake_gui,make,ninja,xcodebuild
from util import color, log

#-------------------------------------------------------------------------------
def print_found(tool) :
    print '{}:\t{}found{}'.format(tool, color.GREEN, color.DEF)

#-------------------------------------------------------------------------------
def print_notfound(tool) :
    print '{}:\t{}NOT FOUND{}'.format(tool, color.RED, color.DEF)

#-------------------------------------------------------------------------------
def check_tools() :
    print '{}=== TOOLS:{}'.format(color.YELLOW, color.DEF)
    tools = [ cmake, ccmake, cmake_gui, make, ninja, xcodebuild ]
    for tool in tools:
        if platform.system() in tool.platforms :
            if tool.check_exists() :
                print_found(tool.name)
            else :
                print_notfound(tool.name)

#-------------------------------------------------------------------------------
def run(args) :
    check_tools()
