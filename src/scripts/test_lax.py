#!/usr/bin/env python3

import yaml
import argparse
import pathlib
from lax_test import LaxTester

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='laxのテストを行う'
        )
    parser.add_argument('test_config_path', help='testを実行するためのconfig')

    args = parser.parse_args()

    test_config_path = pathlib.Path(args.test_config_path)
    
    with open(test_config_path, "r") as f:
        config = yaml.safe_load(f)

    tester = LaxTester(config)
    tester.run_lax_test()