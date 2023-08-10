from typing import Dict,Any
import numpy as np
import math
import time
import pathlib
import subprocess
import glob
import yaml
from limda import SimulationFrame
from limda import SimulationFrames

class LaxTester:
    def __init__(
        self,
        config: dict[str, Any]
    ):
        self.check_and_set_config(config)
        self.config: dict[str, Any] = config

    def run_test(self):
        #configで指定された条件でmdを回し、laichと比較する

        for loop in range(self.config["loop_num"]):
            sf_lax = SimulationFrame("C H O N Si")
            self.random_pack(sf_lax) # 水原子をsfに詰めます。
            sf_laich = SimulationFrame("C H O N Si")
            self.set_input_with_velocity(sf_lax, sf_laich) # 初期速度を持ったinputを作成
            self.run_lax_and_laich(sf_lax, sf_laich) #実際にlaichとlaxを回します. 
            #2つの結果を読み込む
            sf_laich.import_dumppos(self.config["calc_dir"] / f"laich_calc/dump.pos.{self.config['md_config']['TotalStep']}")
            sf_lax.import_dumppos(self.config["calc_dir"] / f"lax_calc/dump.pos.{self.config['md_config']['TotalStep']}")
            #2つの結果を比較
            self.compare_result(sf_lax, sf_laich, f"{loop}")
            if loop != self.config["loop_num"] - 1:
                subprocess.call(f"rm -r {self.config['calc_dir'] / 'packmol_tmp'}".split())
                subprocess.call(f"rm -r {self.config['calc_dir'] / 'laich_calc'}".split())
                subprocess.call(f"rm -r {self.config['calc_dir'] / 'lax_calc'}".split())

    def run_testcases(self):
        # 用意してあるテストケースもmdを回し,laichと比較する

        # testcaseの読み込み
        lax_testcases = glob.glob(f"{self.config['testcases_path']}/lax/*/*/config*") 
        laich_testcases = glob.glob(f"{self.config['testcases_path']}/laich/*/config*")
        # laichのtestcaseを回す。# dump.posを用意しとくだけでいいかも
        answer = self.make_answer_by_laich(laich_testcases)
        # laxのテストケースを一つずつ回していく.
        for testcase in lax_testcases:
            testcase = pathlib.Path(testcase)
            if testcase.parent.name == "move" or testcase.parent.name == "press_move": # moveが完成していないため
                continue
            subprocess.run(f"cp -r {testcase.parent} .".split())
            sf = self.run_lax_testcase(testcase)
            comment = f"MPI {testcase.parent.parent.name} : {testcase.parent.name}"
            # laichのanswerと比較
            self.compare_result(sf, answer[testcase.parent.name], comment)
            subprocess.run(f"rm -r {testcase.parent.name}".split())

    def  check_and_set_config(self, config: Dict[str, Any]):
        """
        md_configのcheck
        """
        assert "calc_dir" in config,"calc_dirを指定してください"
        config["calc_dir"] = pathlib.Path(config["calc_dir"])

        if "loop_num" not in config:
            config["loop_num"]: int = 10
        
        if "cell" not in config:
            config["cell"]: np.array[float] = np.array([20,20,20])

        if "pack_num" not in config:
            config["pack_num"]: int = 30

        if "laich_mask_info" not in config:
            config["laich_mask_info"]: list[str] = None
    
        if "lax_mask_info" not in config:
            config["lax_mask_info"]: list[str] = None

        config["md_config"]["TotalStep"] -= config["md_config"]["TotalStep"] % config["md_config"]["FileStep"]

        config["md_config"]["ReadVelocity"] = 1

    def random_pack(self, sf_lax: SimulationFrame):
        """
        packmolで水原子のランダムな配置を作成
        """
        sf_lax.cell = self.config["cell"]
        sf_H2O = SimulationFrame("C H O N Si")
        sf_H2O.import_mol('H2O') # 水分子のデータを読み込む
        xyz_condition = [
            [0.7, 0.7, 0.7, sf_lax.cell[0] - 0.7, sf_lax.cell[1] - 0.7, sf_lax.cell[2] - 0.7],
        ]
        sf_lax.packmol(sf_list=[sf_H2O,],
                pack_num_list=[self.config["pack_num"],],
                tolerance=1.7, # それぞれの水分子は最低1.7Å離れて配置される
                xyz_condition=xyz_condition, seed=-1) # seed=-1とすると、シードはランダム
        
    def set_input_with_velocity(self, sf_lax: SimulationFrame, sf_laich: SimulationFrame):
        """
        短時間でmdを回し、速度を持ったsfを作成
        """
        pre_config = self.config["md_config"].copy()
        pre_config["TotalStep"] = 1
        pre_config["ReadVelocity"] = 0
        sf_lax.lax(
            calc_dir = "prelax_calc",
            lax_config = pre_config,
            lax_cmd = "~/lax/src/build/lax",
            print_lax = False,
            exist_ok = True,
        )
        sf_lax = SimulationFrame("C H O N Si")
        sf_lax.import_dumppos(self.config["calc_dir"] / "prelax_calc/dump.pos.0")
        sf_laich.import_dumppos(self.config["calc_dir"] / "prelax_calc/dump.pos.0")
        subprocess.call(f"rm -r {self.config['calc_dir'] / 'prelax_calc'}".split())

    def run_lax_and_laich(self, sf_lax: SimulationFrame, sf_laich: SimulationFrame):
        """
        md_configの条件でlaxとlaichを回す
        """
        sf_lax.atoms["mask"] = [i%2 for i in range(len(sf_lax))]
        sf_laich.atoms["mask"] = [i%2 for i in range(len(sf_lax))]

        laich_config = self.config["md_config"].copy()
        laich_config["MPIGridX"] = 1
        laich_config["MPIGridY"] = 1
        laich_config["MPIGridZ"] = 1
        sf_laich.laich(
            calc_dir = "laich_calc",
            laich_config = laich_config,
            laich_cmd = "~/Laich/src/build/laich",
            print_laich = False,
            exist_ok = True,
            mask_info = self.config["laich_mask_info"]
        )
        sf_lax.lax(
            calc_dir = "lax_calc",
            lax_config = self.config["md_config"],
            lax_cmd = "~/lax/src/build/lax",
            print_lax = False,
            exist_ok = True,
            mask_info = self.config["lax_mask_info"],
        )

    def compare_result(self, sf_lax: SimulationFrame, sf_laich: SimulationFrame, comment: str):
        """
        二つのsfを比較する。指定した許容誤差より誤差が大きければエラーを吐き終了する.
        """
        atoms_diff = (sf_laich.atoms - sf_lax.atoms).abs()
        for i,dim in enumerate(["x", "y", "z"]):
            atoms_diff[dim] = [min(diff, math.fabs(diff-sf_lax.cell[i])) for diff in atoms_diff[dim]]
        diff_max = atoms_diff.max()
        judge = True
        for col, val in diff_max.items():
            if not col in self.config["allowable_error"]:
                continue
            if self.config["allowable_error"][col] < val:
                judge = False
        
        if not judge:
            print(f"Error {comment}")
            print(diff_max)
            exit()
        else: 
            print(f"Pass {comment}")

    def run_lax_testcase(self, testcase: pathlib.Path)->SimulationFrame:
        """
        laxのテストケースを回す
        """
        mpi: int = int(testcase.parent.parent.name) # testcase/lax/mpi/typ/config*
        typ: str = testcase.parent.name
        num_process = int(mpi/100) * int((mpi%100)/10) * int(mpi%10)
        cmd = f"mpiexec.hydra -np {num_process} ~/lax/src/build/lax {testcase.name} < /dev/null >& out"
        lax_process = subprocess.Popen(cmd, cwd = self.config["calc_dir"] / typ, shell = True)
        while lax_process.poll() is None:
            time.sleep(1)
        sf = SimulationFrame("C H O N Si")
        sf.import_dumppos(self.config["calc_dir"] / f"{typ}/dump.pos.100")
        return sf  
    
    def make_answer_by_laich(self, testcases: str)->dict[SimulationFrame]:
        """
        laichのテストケースを回す.
        """
        answer: dict[SimulationFrame] = {}
        for testcase in testcases:
            testcase = pathlib.Path(testcase)
            typ: str = testcase.parent.name
            subprocess.run(f"cp -r {testcase.parent} .".split())
            cmd = f"mpiexec.hydra -np 1 ~/Laich/src/build/laich {testcase.name} < /dev/null >& out"
            laich_process = subprocess.Popen(cmd, cwd = self.config["calc_dir"] / typ, shell = True)
            while laich_process.poll() is None:
                time.sleep(1)
            sf = SimulationFrame("C H O N Si")
            sf.import_dumppos(self.config["calc_dir"] / f"{typ}/dump.pos.100")
            answer[typ] = sf
            subprocess.run(f"rm -r {typ}".split())
        return answer
            