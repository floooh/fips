'''this is just a dummy tool to check if the VSCode CMake Tools is installed'''
import subprocess
import platform
from mod.tools import vscode

name = 'vscode-cmaketools'
platforms = ['osx','linux','win']
optional = True
not_found = 'https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    return vscode.has_extension('ms-vscode.cmake-tools')
