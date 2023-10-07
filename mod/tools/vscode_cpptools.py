'''this is just a dummy tool to check if the VSCode C/C++ Extension is installed'''
import subprocess
import platform
from mod.tools import vscode

name = 'vscode-cpptools'
platforms = ['osx','linux','win']
optional = True
not_found = 'https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    return vscode.has_extension('ms-vscode.cpptools')
