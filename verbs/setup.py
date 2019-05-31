"""'setup' verb to setup platform SDKs

setup emscripten
setup android
"""

from mod import log, emsdk, android

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    """run the 'setup' verb"""
    sdk_name = None
    if len(args) > 0 :
        sdk_name = args[0]
    if sdk_name == 'emscripten' :
        emsdk.install(fips_dir, None)
    elif sdk_name == 'android' :
        android.setup(fips_dir, proj_dir)
    else :
        log.error("invalid SDK name (must be 'emscripten' or 'android')")

#-------------------------------------------------------------------------------
def help() :
    """print help text for init verb"""
    log.info(log.YELLOW +
             "fips setup emscripten\n"
             "fips setup android\n"
             + log.DEF +
             "    setup cross-platform SDK") 
    
        
