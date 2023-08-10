#!/usr/bin/env python3

import yaml
import argparse
import pathlib
from lax_test import LaxTester
from limda import SimulationFrame

# run lax test
"""
laichとlaxを同じ条件で回し、結果を比較する

-------------------------------------
    calc_dir : テストを実行するディレクトリ

    loop_num : 何回テストを実行するか

    cell : テストに使う系のcellサイズ、defaultは[20,20,20]

    pack_num : H2Oをセルに何個詰めるか、defalultは30

    laich_mask_info : laichのinputにかかれるpressやmoveの情報

    lax_mask_info : laxのinputにかかれるpressやmoveの情報

    allowable_error : laxとlaichの結果に対する許容誤差

    md_config : laich,laxのconfigにかかれる
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='laxとlaichのテストを実行する'
        )
    parser.add_argument('md_config_path', help='mdを実行するためのconfig')

    args = parser.parse_args()

    md_config_path = pathlib.Path(args.md_config_path)
    
    with open(md_config_path, "r") as f:
        config = yaml.safe_load(f)

    tester = LaxTester(config)
    tester.run_test()
