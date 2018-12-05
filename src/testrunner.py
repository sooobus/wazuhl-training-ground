from src import config
import random
from tqdm import tqdm

def get_tests(suites, flags):
    tests = []
    for suite in suites:
        print("suite", suite)
        suite.configure(config.get_clang(), config.get_clangpp(), flags, flags)
        print("Configured suite and want to grab tests from it")
        tests.extend(suite.get_tests())
        print(len(suite.get_tests()))
        print(len(tests))
    return tests

def run(tests):
    for test in tqdm(tests):
        run_test(test)
    return tests

def run_random(tests):
    assert len(tests) > 0, "Please provide some tests to run_random"
    test = random.choice(tests)
    return run_test(test)

def run_test(test):
    test.compile()
    test.run()
    return test
