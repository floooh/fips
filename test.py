
import unittest
import shutil
import os

from tools import cmake
from tools import ccmake

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

    def test_check(self) :
        self.assertTrue(cmake.check())

    def test_run_gen(self) :
        self.assertTrue(self.generate())

    def test_run_build(self) :
        self.assertTrue(self.generate())
        self.assertTrue(self.build())

#-------------------------------------------------------------------------------
class ccmake_testcase(unittest.TestCase) :

    def setUp(self) :
        ensure_dir('build/ccmake_testcase')

    def test_check(self) :
        self.assertTrue(ccmake.check())

    def test_run(self) :
        buildDir = make_path('build/ccmake_testcase')
        self.assertTrue(cmake.run_gen(
            generator = 'Unix Makefiles',
            build_type = 'Release',
            defines = None,
            toolchain_path = None,
            build_dir = buildDir,
            project_dir = make_path('proj')))
        self.assertTrue(ccmake.run(buildDir))


unittest.main()






