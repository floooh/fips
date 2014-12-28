
import unittest
import shutil
import os
import platform

from mod.tools import cmake,ccmake,cmake_gui,make,ninja,xcodebuild,git
from mod import config

root_path = os.path.dirname(os.path.abspath(__file__))

#-------------------------------------------------------------------------------
def make_path(tail) :
    return root_path + '/test/' + tail 

#-------------------------------------------------------------------------------
def ensure_dir(dirname) :
    path = make_path(dirname)
    if os.path.exists(path) :
        shutil.rmtree(path)
    os.makedirs(path)

#-------------------------------------------------------------------------------
class cmake_testcase(unittest.TestCase) :

    def setUp(self) :
        ensure_dir('build/cmake_testcase')

    def generate(self) :
        cfg = {
            'generator': 'Unix Makefiles',
            'build_type': 'Release',
            'defines': None,
            'name': 'test-test-test',
        }
        proj_dir = make_path('proj')
        build_dir = make_path('build/cmake_testcase')
        return cmake.run_gen(cfg, proj_dir, build_dir, None)

    def build(self) :
        return cmake.run_build(
            build_type = 'Release',
            build_dir = make_path('build/cmake_testcase'))
    def clean(self) :
        return cmake.run_clean(build_dir=make_path('build/cmake_testcase'))

    def test_exists(self) :
        self.assertTrue(cmake.check_exists())

    def test_run_gen(self) :
        self.assertTrue(self.generate())

    def test_run_build(self) :
        self.assertTrue(self.generate())
        self.assertTrue(self.build())
        self.assertTrue(self.clean())
        self.assertTrue(self.build())

#-------------------------------------------------------------------------------
class ccmake_testcase(unittest.TestCase) :

    def setUp(self) :
        ensure_dir('build/ccmake_testcase')

    def test_exists(self) :
        if platform.system() in ['Linux', 'Darwin'] :
            self.assertTrue(ccmake.check_exists())

#-------------------------------------------------------------------------------
class cmake_gui_testcase(unittest.TestCase) :

    def setUp(self) :
        ensure_dir('build/cmake_gui_testcase')

    def test_exists(self) :
        if platform.system() == 'Windows' :
            self.assertTrue(cmake_gui.check_exists())

#-------------------------------------------------------------------------------
class make_testcase(unittest.TestCase) :

    def setUp(self) :
        ensure_dir('build/make_testcase')

    def test_exists(self) :
        if platform.system() in ['Linux', 'Darwin'] :
            self.assertTrue(make.check_exists())

    def test_run(self) :
        if platform.system() in ['Linux', 'Darwin'] :
            cfg = {
                'generator': 'Unix Makefiles',
                'build_type': 'Release',
                'defines': None,
                'name': 'test-test-test',
            }
            proj_dir = make_path('proj')
            build_dir = make_path('build/make_testcase')
            self.assertTrue(cmake.run_gen(cfg, proj_dir, build_dir, None))
            self.assertTrue(make.run_build(target=None, build_dir=build_dir))
            self.assertTrue(make.run_clean(build_dir=build_dir))
            self.assertTrue(make.run_build(target='hello', build_dir=build_dir, num_jobs=3))

#-------------------------------------------------------------------------------
class ninja_testcase(unittest.TestCase) :

    def setUp(self) :
        ensure_dir('build/ninja_testcase')

    def test_exists(self) :
        if platform.system() in ['Linux', 'Darwin'] :
            self.assertTrue(ninja.check_exists())

    def test_run(self) :
        if platform.system() in ['Linux', 'Darwin'] :
            cfg = {
                'generator': 'Ninja',
                'build_type': 'Release',
                'defines': None,
                'name': 'test-test-test',
            }
            proj_dir = make_path('proj')
            build_dir = make_path('build/ninja_testcase')
            self.assertTrue(cmake.run_gen(cfg, proj_dir, build_dir, None))
            self.assertTrue(ninja.run_build(target=None, build_dir=build_dir))
            self.assertTrue(ninja.run_clean(build_dir=build_dir))
            self.assertTrue(ninja.run_build(target='hello', build_dir=build_dir, num_jobs=3))

#-------------------------------------------------------------------------------
class xcodebuild_testcase(unittest.TestCase) :

    def setUp(self) :
        ensure_dir('build/xcodebuild_testcase')

    def test_exists(self) :
        if platform.system() == 'Darwin' :
            self.assertTrue(xcodebuild.check_exists())

    def test_run(self) :
        if platform.system() == 'Darwin' :
            cfg = {
                'generator': 'Xcode',
                'build_type': 'Release',
                'defines': None,
                'name': 'test-test-test',
            }
            proj_dir = make_path('proj')
            build_dir = make_path('build/xcodebuild_testcase')
            self.assertTrue(cmake.run_gen(cfg, proj_dir, build_dir, None))
            self.assertTrue(xcodebuild.run_build(
                target = None, 
                build_type = 'Release', 
                build_dir = build_dir))
            self.assertTrue(xcodebuild.run_clean(build_dir))
            self.assertTrue(xcodebuild.run_build(
                target = 'hello', 
                build_type = 'Release', 
                build_dir = build_dir, 
                num_jobs = 3))
                    
#-------------------------------------------------------------------------------
class git_testcase(unittest.TestCase) :

    def setUp(self) :
        ensure_dir('build/git_testcase')

    def test_exists(self) :
        self.assertTrue(git.check_exists())

    def test_clone(self) :
        test_dir = make_path('build/git_testcase')
        self.assertTrue(git.clone(
            url = 'git@github.com:floooh/fips.git',
            branch = 'master',
            name = 'fips',
            cwd = test_dir))
        self.assertTrue(os.path.isfile(test_dir + '/fips/test.py'))

#-------------------------------------------------------------------------------
class config_testcase(unittest.TestCase) :

    def test_valid_platform(self) :
        platforms = ['osx', 'win32', 'win64', 'linux', 'emscripten', 'pnacl', 'ios', 'android']
        for p in platforms :
            self.assertTrue(config.valid_platform(p))

    def test_valid_generator(self) :
        generators = ['Unix Makefiles', 'Ninja', 'Xcode', 'Visual Studio 12', 'Visual Studio 12 Win64']
        for gen in generators :
            self.assertTrue(config.valid_generator(gen))
        self.assertFalse(config.valid_generator('Bla'))
    
    def test_valid_build_tool(self) :
        tools = ['make', 'ninja', 'xcodebuild', 'cmake']
        for tool in tools :
            self.assertTrue(config.valid_build_tool(tool))
        self.assertFalse(config.valid_build_tool('bla'))

    def test_valid_build_type(self) :
        build_types = ['Release', 'Debug', 'Profiling']
        for t in build_types :
            self.assertTrue(config.valid_build_type(t))
        self.assertFalse(config.valid_build_type('bla'))

    def test_get_host_platform(self) :
        self.assertTrue(config.get_host_platform() in ['osx', 'win', 'linux'])

    def test_exists(self) :
        cfg_dirs = [root_path]

        self.assertTrue(config.exists('osx-make-debug', cfg_dirs))
        self.assertTrue(config.exists('osx-make-release', cfg_dirs))
        self.assertTrue(config.exists('osx-make-*', cfg_dirs))
        self.assertTrue(config.exists('*-make-*', cfg_dirs))
        self.assertFalse(config.exists('blub-make-debug', cfg_dirs))

    def test_load(self) :
        cfg_dirs = [root_path]
        cfg = config.load('osx-make-debug', cfg_dirs)
        self.assertEqual(len(cfg), 1)
        self.assertEqual(cfg[0]['name'], 'osx-make-debug')
        self.assertEqual(cfg[0]['build_tool'], 'make')
        self.assertEqual(cfg[0]['platform'], 'osx')
        self.assertEqual(cfg[0]['build_type'], 'Debug')
        self.assertEqual(cfg[0]['generator'], 'Unix Makefiles')
        cfg = config.load('osx-make-*', cfg_dirs)
        self.assertEqual(len(cfg), 2)

    def test_list(self) :
        cfg_dirs = [root_path + '/configs']
        cfg = config.list('osx-*', cfg_dirs)
        self.assertTrue(len(cfg), 2)

    def test_check_config_valid(self) :
        cfg = config.load('osx-make-debug', [root_path])[0]
        self.assertTrue(config.check_config_valid(cfg))


#===============================================================================        
unittest.main()






