from typing import Dict,Any
import numpy as np
import math
import time
import pathlib
import subprocess
from limda import SimulationFrame

class LaxTester:
    def __init__(
        self,
        config: dict[str, Any]
    ):
        self.check_and_set_config(config)
        self.config: dict[str, Any] = config
        self.sf: SimulationFrame = None

    def compare_lax_and_laich(self):
        for loop in range(self.config["loop_num"]):
            self.sf = SimulationFrame("C H O N Si")
            # 水原子をsfに詰めます。
            self.random_pack()
            # 短時間MDを回すことにより、
            # 初期速度を持ったinputを作成できるようにします。
            sf_laich = SimulationFrame("C H O N Si")
            self.set_input_with_velocity(sf_laich)
            #実際にlaichとlaxを回します.

            self.sf.atoms["mask"] = [i%2 for i in range(len(self.sf))]
            sf_laich.atoms["mask"] = [i%2 for i in range(len(self.sf))]

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
            self.sf.lax(
                calc_dir = "lax_calc",
                lax_config = self.config["md_config"],
                lax_cmd = "~/lax/src/build/lax",
                print_lax = False,
                exist_ok = True,
                mask_info = self.config["lax_mask_info"],
            )           
            #2つの結果をimportします。
            sf_laich.import_dumppos(self.config["calc_dir"] / f"laich_calc/dump.pos.{self.config['md_config']['TotalStep']}")
            self.sf.import_dumppos(self.config["calc_dir"] / f"lax_calc/dump.pos.{self.config['md_config']['TotalStep']}")
            
            #2つの結果を比較します.
            atoms_diff = (sf_laich.atoms - self.sf.atoms).abs()
            for i,dim in enumerate(["x", "y", "z"]):
                atoms_diff[dim] = [min(diff, math.fabs(diff-self.sf.cell[i])) for diff in atoms_diff[dim]]
            print(f"----- {loop} -----")
            print(atoms_diff.max())

            if loop != self.config["loop_num"] - 1:
                subprocess.call(f"rm -r {self.config['calc_dir'] / 'packmol_tmp'}".split())
                subprocess.call(f"rm -r {self.config['calc_dir'] / 'laich_calc'}".split())
                subprocess.call(f"rm -r {self.config['calc_dir'] / 'lax_calc'}".split())

    def  check_and_set_config(self, config: Dict[str, Any]):
        """configのcheck
        """
        assert "calc_dir" in config,"calc_dirを指定してください"
        config["calc_dir"] = pathlib.Path(config["calc_dir"])
        assert "md_config" in config, "md_configを指定してください"

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

    def random_pack(self):
        self.sf.cell = self.config["cell"]
        sf_H2O = SimulationFrame("C H O N Si")
        sf_H2O.import_mol('H2O') # 水分子のデータを読み込む
        xyz_condition = [
            [0.7, 0.7, 0.7, self.sf.cell[0] - 0.7, self.sf.cell[1] - 0.7, self.sf.cell[2] - 0.7],
        ]
        self.sf.packmol(sf_list=[sf_H2O,],
                pack_num_list=[self.config["pack_num"],],
                tolerance=1.7, # それぞれの水分子は最低1.7Å離れて配置される
                xyz_condition=xyz_condition, seed=-1) # seed=-1とすると、シードはランダム
        
    def set_input_with_velocity(self, sf_laich: SimulationFrame):
        pre_config = self.config["md_config"].copy()
        pre_config["TotalStep"] = 1
        pre_config["ReadVelocity"] = 0
        self.sf.lax(
            calc_dir = "prelax_calc",
            lax_config = pre_config,
            lax_cmd = "~/lax/src/build/lax",
            print_lax = False,
            exist_ok = True,
        )
        self.sf = SimulationFrame("C H O N Si")
        self.sf.import_dumppos(self.config["calc_dir"] / "prelax_calc/dump.pos.0")
        sf_laich.import_dumppos(self.config["calc_dir"] / "prelax_calc/dump.pos.0")
        subprocess.call(f"rm -r {self.config['calc_dir'] / 'prelax_calc'}".split())


