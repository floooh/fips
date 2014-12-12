
import unittest
import shutil
import os
import platform

from tools import cmake,ccmake,cmake_gui,make,ninja,xcodebuild,git

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
        return cmake.run_gen(
            generator = 'Unix Makefiles',
            build_type = 'Release',
            defines = None,
            toolchain_path = None,
            build_dir = make_path('build/cmake_testcase'),
            project_dir = make_path('proj'))

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

    def test_run(self) :
        if platform.system() in ['Linux', 'Darwin'] :
            buildDir = make_path('build/ccmake_testcase')
            self.assertTrue(cmake.run_gen(
                generator = 'Unix Makefiles',
                build_type = 'Release',
                defines = None,
                toolchain_path = None,
                build_dir = buildDir,
                project_dir = make_path('proj')))
            self.assertTrue(ccmake.run(buildDir))

#-------------------------------------------------------------------------------
class cmake_gui_testcase(unittest.TestCase) :

    def setUp(self) :
        ensure_dir('build/cmake_gui_testcase')

    def test_exists(self) :
        if platform.system() == 'Windows' :
            self.assertTrue(cmake_gui.check_exists())

    def test_run(self) :
        if platform.system() == 'Windows' :
            buildDir = make_path('build/cmake_gui_testcase')
            self.assertTrue(cmake.run_gen(
                generator = 'Unix Makefiles',
                build_type = 'Release',
                defines = None,
                toolchain_path = None,
                build_dir = buildDir,
                project_dir = make_path('proj')))
            self.assertTrue(cmake_gui.run(buildDir))

#-------------------------------------------------------------------------------
class make_testcase(unittest.TestCase) :

    def setUp(self) :
        ensure_dir('build/make_testcase')

    def test_exists(self) :
        if platform.system() in ['Linux', 'Darwin'] :
            self.assertTrue(make.check_exists())

    def test_run(self) :
        if platform.system() in ['Linux', 'Darwin'] :
            buildDir = make_path('build/make_testcase')
            self.assertTrue(cmake.run_gen(
                generator = 'Unix Makefiles',
                build_type = 'Release',
                defines = None,
                toolchain_path = None,
                build_dir = buildDir,
                project_dir = make_path('proj')))
            self.assertTrue(make.run_build(target=None, build_dir=buildDir))
            self.assertTrue(make.run_clean(build_dir=buildDir))
            self.assertTrue(make.run_build(target='hello', build_dir=buildDir, num_jobs=3))

#-------------------------------------------------------------------------------
class ninja_testcase(unittest.TestCase) :

    def setUp(self) :
        ensure_dir('build/ninja_testcase')

    def test_exists(self) :
        if platform.system() in ['Linux', 'Darwin'] :
            self.assertTrue(ninja.check_exists())

    def test_run(self) :
        if platform.system() in ['Linux', 'Darwin'] :
            buildDir = make_path('build/ninja_testcase')
            self.assertTrue(cmake.run_gen(
                generator = 'Ninja',
                build_type = 'Release',
                defines = None,
                toolchain_path = None,
                build_dir = buildDir,
                project_dir = make_path('proj')))
            self.assertTrue(ninja.run_build(target=None, build_dir=buildDir))
            self.assertTrue(ninja.run_clean(build_dir=buildDir))
            self.assertTrue(ninja.run_build(target='hello', build_dir=buildDir, num_jobs=3))

#-------------------------------------------------------------------------------
class xcodebuild_testcase(unittest.TestCase) :

    def setUp(self) :
        ensure_dir('build/xcodebuild_testcase')

    def test_exists(self) :
        if platform.system() == 'Darwin' :
            self.assertTrue(xcodebuild.check_exists())

    def test_run(self) :
        if platform.system() == 'Darwin' :
            buildDir = make_path('build/xcodebuild_testcase')
            self.assertTrue(cmake.run_gen(
                generator = 'Xcode',
                build_type = 'Release',
                defines = None,
                toolchain_path = None,
                build_dir = buildDir,
                project_dir = make_path('proj')))
            self.assertTrue(xcodebuild.run_build(
                target = None, 
                build_type = 'Release', 
                build_dir = buildDir))
            self.assertTrue(xcodebuild.run_clean(buildDir))
            self.assertTrue(xcodebuild.run_build(
                target = 'hello', 
                build_type = 'Release', 
                build_dir = buildDir, 
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
            name = 'fips',
            cwd = test_dir))
        self.assertTrue(os.path.isfile(test_dir + '/fips/test.py'))

#===============================================================================        
unittest.main()






