import pickle
import os

from src import config
from src import testrunner
from src import utils


class Reinforcer:
    def __init__(self, suites):
        self.suites = suites
        self.alpha = config.get_alpha()
        self.tests = []

        self.baselines = {"compile_time": {}, "execution_time": {}}

    def init_baselines(self, compilation, execution):
        self.measure_baseline("compilation", compilation, "compile_time")
        self.measure_baseline("execution", execution, "execution_time", compilation != execution)

    def measure_baseline(self, name, flags, test_attr, rerun=True):
        print("Measuring baseline")
        cache_file = Reinforcer.__etalon_file__(name, flags)
        results = {} #self.__load_cache__(cache_file)
        if not results:
            results = {}
            if rerun or not self.tests:
                self.tests = testrunner.get_tests(self.suites, flags)
                self.tests = testrunner.run(self.tests)

            print("38")
            for test in self.tests:
                self.baselines["compile_time"][test.name] = test.compile_time
                self.baselines["execution_time"][test.name] = test.execution_time

            self.__cache__(results, cache_file)
        print("baselines")
        print(self.baselines)
        self.__check__(self.tests)

    def calculate_reward(self, test):
        C = self.baselines["compile_time"][test.name]
        E = self.baselines["execution_time"][test.name]
        alpha = self.alpha
        Cp = test.compile_time
        Ep = test.execution_time
        print(Cp, Ep)
        if not Cp or not Ep: return -1
        return (E - Ep) / E + alpha * (C - Cp) / C

    def run(self):
        print("Reinforcer running. Getting tests")
        tests = testrunner.get_tests(self.suites, '-OW -ftrain-wazuhl')
        print("Got tests")
        print("Before check", len(tests))
        self.__check__(tests)
        print("Checked tests")
        print(self.baselines)
        #while (True):
        #    result = testrunner.run_random(tests)
        #    print("Result: ", self.calculate_reward(result))

    def __check__(self, tests):
        tests = set(map(str, tests))
        compilation_tests = set(self.baselines["compile_time"].keys())
        execution_tests = set(self.baselines["execution_time"].keys())
        print(tests, compilation_tests, execution_tests)
        message = "Ethalon tests ({0}) differ from the ones for Wazuhl!"
        if tests != compilation_tests:
            utils.error(message.format("compilation"))
        if tests != execution_tests:
            utils.error(message.format("execution"))
        assert len(tests) > 0, "Test suite is empty!"

    def __cache__(self, data, cache_file):
        with open(cache_file, 'wb') as cache:
            pickle.dump(data, cache)

    def __load_cache__(self, cache_file):
        if not os.path.exists(cache_file):
            return None
        with open(cache_file, 'rb') as cache:
            return pickle.load(cache)

    @staticmethod
    def __etalon_file__(name, flags):
        return os.path.join(config.get_output(),
                            "{0}.{1}.etalon".format(name, utils.pathify(flags)))
