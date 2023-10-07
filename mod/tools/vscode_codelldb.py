'''this is just a dummy tool to check if the VSCode CodeLLDB Extension is installed'''
import subprocess
import platform
from mod.tools import vscode

name = 'vscode-codelldb'
platforms = ['osx','linux','win']
optional = True
not_found = 'https://marketplace.visualstudio.com/items?itemName=vadimcn.vscode-lldb'

#------------------------------------------------------------------------------
def check_exists(fips_dir) :
    return vscode.has_extension('vadimcn.vscode-lldb')
