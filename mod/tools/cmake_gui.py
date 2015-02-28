"""wrap the ccmake-gui tools (Windows only)"""
import subprocess

name = 'cmake-gui'
platforms = ['win']
optional = True
not_found = "required for 'fips config' functionality"

#-------------------------------------------------------------------------------
def check_exists(fips_dir) :
    """test if cmake-gui is in the path
    
    :returns:   True if cmake-gui is in the path
    """
    try:
        out = subprocess.check_output(['cmake-gui', '--version'])
        return True
    except (OSError, subprocess.CalledProcessError) :
        return False;
        
#-------------------------------------------------------------------------------
def run(build_dir) :
    """run the cmake-gui tool

    :params build_dir:  directory where cmake-generated build files are located
    :returns:           True if cmake-gui returns successful
    """
    res = subprocess.call('cmake-gui .', cwd=build_dir, shell=True)
    return res == 0
    
