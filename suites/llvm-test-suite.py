import os
import re
import shutil
import subprocess
from src import config, utils

class Suite:
    name = "llvm-test-suite"
    def __init__(self):
        self.tests = []

    def get_tests(self):
        print("returning tests", len(self.tests))
        return self.tests

    def configure(self, CC, CXX, COPTS, CXXOPTS):
        output = config.get_output()
        suite = os.path.join(output, self.name)

        print(suite)

        suite = '/home/valeriia/tr_gr/suites/test-suite'

        self.build = '/home/valeriia/tr_gr/suites/llvm-test-suite-build'
        if os.path.exists(self.build):
            shutil.rmtree(self.build)
        os.makedirs(self.build)
        self.go_to_builddir()

        self.configuration_env = os.environ.copy()
        self.configuration_env['CC'] = CC
        self.configuration_env['CXX'] = CXX
        self.configuration_env['LD_LIBRARY_PATH'] = '/home/valeriia/caffe/build/lib/:'

        make_command = ['cmake', '/home/valeriia/tr_gr/suites/test-suite',
                             '-DCMAKE_BUILD_TYPE=Release',
                             '-DCMAKE_C_FLAGS_RELEASE={0}'.format(COPTS),
                             '-DCMAKE_CXX_FLAGS_RELEASE={0}'.format(CXXOPTS)]
        print(make_command)
        with open(os.devnull, 'wb') as devnull:
            cmake_output = subprocess.Popen(make_command, env=self.configuration_env, stdout=subprocess.PIPE)
            out = cmake_output.stdout.read().decode('utf-8')
            #print(out)

        print("Configuration is finished")

        self.__init_tests__()

    def __init_tests__(self):
        utils.check_executable('lit')
        #print('LIT')
        #print(os.listdir('/wazuhl-polygon/suites/llvm-test-suite'))
        #print('LIT')
        lit = subprocess.Popen(['lit', '--show-tests', '/home/valeriia/tr_gr/suites/llvm-test-suite-build'], stdout=subprocess.PIPE)
        output = lit.stdout.read().decode('utf-8')
        pattern = r'test-suite :: (.*)'
        results = re.findall(pattern, output)
        self.build = "/home/valeriia/tr_gr/suites/llvm-test-suite-build/"
        print("in the end of init tests")
        self.tests = [Test(os.path.join(self.build, test), self) for test in results]
        print("len tests", len(self.tests))
        self.tests = [test for test in self.tests if "Benchmark" in test.path]
        print("len tests", len(self.tests))

    def go_to_builddir(self):
        os.chdir(self.build)

class Test:
    def __init__(self, path, suite):
        self.path = path
        self.name = Test.__get_test_name__(path)
        self.suite = suite

    @staticmethod
    def __get_test_name__(path):
        _, test_file = os.path.split(path)
        test, _ = os.path.splitext(test_file)
        return test

    def compile(self):
        self.suite.go_to_builddir()
        with open(os.devnull, 'wb') as devnull:
            #,  'VERBOSE=1'
            make_output = subprocess.Popen(['make', '-j5', self.name], env=self.suite.configuration_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = make_output.stdout.read().decode('utf-8')
            #print(out)

    def run(self):
        test_run = subprocess.Popen(['lit', self.path], stdout=subprocess.PIPE)
        output = test_run.stdout.read().decode('utf-8')
        #print(output)
        compile_pattern = r'compile_time: (.*)'
        execution_pattern = r'exec_time: (.*)'
        compile_time = re.search(compile_pattern, output)
        if compile_time: compile_time = float(compile_time.group(1))
        execution_time = re.search(execution_pattern, output)
        if execution_time: execution_time = float(execution_time.group(1))
        self.compile_time, self.execution_time = compile_time, execution_time

    def __str__(self):
        return self.name
