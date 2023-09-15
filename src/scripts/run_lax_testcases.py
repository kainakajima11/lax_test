#!/usr/bin/env python3

import yaml
import argparse
import pathlib
from lax_test import OldLaxTester
from limda import SimulationFrame

# run lax testcases
"""
    calc_dir : テストを実行するディレクトリ

    testcases_path : lax_test内のtestcase ディレクトリの場所

    allowable_error : laxとlaichの結果に対する許容誤差
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='laxとlaichのテストケースを実行する'
        )
    parser.add_argument('md_config_path', help='mdを実行するためのconfig')

    args = parser.parse_args()

    md_config_path = pathlib.Path(args.md_config_path)
    
    with open(md_config_path, "r") as f:
        config = yaml.safe_load(f)

    tester = OldLaxTester(config)
    tester.run_testcases()