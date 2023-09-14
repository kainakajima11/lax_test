#!/usr/bin/env python3

import yaml
import argparse
import pathlib
from lax_test import NewLaxTester

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='laxとlaichのテストケースを実行する'
        )
    parser.add_argument('md_config_path', help='mdを実行するためのconfig')

    args = parser.parse_args()

    md_config_path = pathlib.Path(args.md_config_path)
    
    with open(md_config_path, "r") as f:
        config = yaml.safe_load(f)

    tester = NewLaxTester(config)
    tester.run_lax_test()