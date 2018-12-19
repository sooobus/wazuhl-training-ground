#!/usr/bin/python

import logging

from suites import suites
from src import options
from src.reinforcer import Reinforcer


def main():
    options.parse()
    logging.basicConfig(level=logging.INFO)
    reinforcer = Reinforcer(suites.get_suites())
    reinforcer.measure_baseline('-O2')
    reinforcer.run()


if __name__ == "__main__":
    main()