import numpy as np
from typing import Any
import numpy.typing as npt
import pathlib
from copy import deepcopy
from limda import SimulationFrame
from .tester_methods import TesterMethods
from .md_info import MDInfo

class LaxTester(TesterMethods):
    config: dict[str, Any]
    laich: SimulationFrame
    laich_energy: npt.NDArray[np.float64]
    lax: SimulationFrame
    lax_energy: npt.NDArray[np.float64]
    atoms_diff: dict[str, float]
    cell_diff: npt.NDArray[np.float64]
    energy_diff: npt.NDArray[np.float64]

    def __init__(self, config: dict[str ,Any]):
        self.config: dict[str, Any] = config

    def run_lax_test(self):
        """
        laxのtestを実行する
        """
        # testのconfigをcheck
        self.check_and_set_config()

        # make dir
        self.config["calc_dir"].mkdir()
        pathlib.Path(self.config["calc_dir"] / "laich").mkdir()
        pathlib.Path(self.config["calc_dir"] / "lax").mkdir()
        if "set_initial_velocity" in self.config:
            pathlib.Path(self.config["calc_dir"] / "initial_velo").mkdir()

        # 実行するmdのlistを作成
        md_list = self.get_md_list()

        # mdを実行、比較
        for md in md_list:
            # laich
            self.calculate_by_laich(md)

            #lax
            for omp, mpi in zip(self.config["OMPGrid"], self.config["MPIGrid"]):
                self.calculate_by_lax(md, omp, mpi)

                # 結果を比較
                self.compare_result(md, omp, mpi)
    
    def check_and_set_config(self):
        """
        tester_configが必要な情報を含んでないかや、
        不適切な形式でないかcheckする。
        また入力がなかった部分にdefault値をsetする.
        """
        cf = self.config
        assert cf["mode"] == "free" #  or cf["mode"] == "testcase" or cf["mode"] == "random" # todo

        # calc_path
        if not cf["calc_dir"]:
            cf["calc_dir"] = "lax_test_calc"
        cf["calc_dir"] = pathlib.Path(cf["calc_dir"])

        # free
        if cf["mode"] == "free":
            # check input_paths, input_names
            assert cf["input_paths"]
            input_len = len(cf["input_paths"])
            if not cf["input_names"]:
                cf["input_names"] = [i for i, _ in enumerate(cf["input_paths"])]
            assert input_len == len(cf["input_names"])

            # mask_info, mask_info_names
            if not cf["mask_info"]:
                cf["mask_info"] = [[]]
            if not cf["mask_info_names"]:
                cf["mask_info_names"] = [i for i, _ in enumerate(cf["mask_info"])]
            assert len(cf["mask_info"]) == len(cf["mask_info_names"])

            # omp
            if not cf["OMPGrid"]:
                cf["OMPGrid"] = [111]
            for omp in cf["OMPGrid"]:
                assert 99 < omp and omp < 1000
                assert str(omp)[0] != "0" and str(omp)[1] != "0" and str(omp)[2] != "0" 

            # mpi
            if not cf["MPIGrid"]:
                cf["MPIGrid"] = [111]
            for mpi in cf["MPIGrid"]:
                assert 99 < mpi and mpi < 1000
                assert str(mpi)[0] != "0" and str(mpi)[1] != "0" and str(mpi)[2] != "0"
            
            # md_config
            assert cf["md_config"]
            for lst in cf["md_config"].values():
                assert len(lst) == 1 or len(lst) == input_len

            # set_initial_velocity
            if not "set_initial_velocity" in cf:
                cf["set_initial_velocity"] = 0

    def get_md_list(self)->list[MDInfo]:
        """
        計算を実行するmdのリストを作成する.
        リストはMDに関する情報を持つMDInfoを要素とする.
        """
        md_list = []
        for mask_info, mask_info_name in zip(self.config["mask_info"], self.config["mask_info_names"]):
            for input_id, [input_path, input_name] in enumerate(zip(self.config["input_paths"], self.config["input_names"])):
                md = MDInfo(self.config["para"][input_id],
                            input_path,
                            mask_info,
                            f"{input_name}_{mask_info_name}",
                            self.config["md_config"],
                            input_id)

                if self.config["set_initial_velocity"]:
                    self.set_initial_velocity(md)

                md_list.append(md)
        return md_list
        
    def calculate_by_laich(self, md: MDInfo):
        """
        laichによってMDを実行する.
        計算後、構造がsfとしてself.laichに
        エネルギーや温度がlist[float]としてself.laich_energyに入る
        """
        self.laich = SimulationFrame()
        self.laich.import_para_from_list(md.para)
        self.laich.import_file(md.input_path)
        laich_md = deepcopy(md)
        laich_md.set_laich()
        self.laich.laich(calc_dir = self.config["calc_dir"] / "laich" / laich_md.name,
                         laich_config = laich_md.config,
                         print_laich = True,
                         exist_ok = True,
                         laich_cmd = self.config["laich_cmd"],
                         mask_info = laich_md.mask_info,
                         )
        self.laich.import_dumppos(self.config["calc_dir"] / "laich" / f"{laich_md.name}" / f"dump.pos.{laich_md.config['TotalStep']}")
        # 結果からenergyを抜き取る
        self.laich_energy = \
            self.get_energy_from_out(self.config["calc_dir"] / "laich" / laich_md.name / "out",
                                     md)
        # unit adjustment
        self.laich_energy[1] *= 1 / 23.060553
        self.laich_energy[2] *= 1 / 23.060553

    def calculate_by_lax(self, md: MDInfo, omp: int, mpi: int):
        """
        laxによってMDを実行する.
        計算後、構造がsfとしてself.laxに
        エネルギーや温度がlist[float]としてself.lax_energyに入る
        """
        self.lax = SimulationFrame()
        self.lax.import_para_from_list(md.para)
        self.lax.import_file(md.input_path)
        md.set_lax(omp, mpi)
        self.lax.lax(calc_dir = self.config["calc_dir"] / "lax" / f"{md.name}_{omp}_{mpi}",
                     lax_config = md.config,
                     print_lax = True,
                     exist_ok = True,
                     lax_cmd = self.config["lax_cmd"],
                     mask_info = md.mask_info
                     )
        self.lax.import_dumppos(self.config["calc_dir"] / "lax" / f"{md.name}_{omp}_{mpi}" / f"dump.pos.{md.config['TotalStep']}")
        # 結果からenergyを抜き取る
        self.lax_energy = \
            self.get_energy_from_out(self.config["calc_dir"] / "lax" / f"{md.name}_{omp}_{mpi}" / "out",
                                     md)

    def compare_result(self, md: MDInfo, omp: int, mpi: int):
        """
        self.laichとself.lax,
        self.laich_energyとself.lax_energyを比較する.
        """
        judge = True 
        # sf.atoms 
        if not self.check_atoms_diff():
            judge = False
        
        # sf.cell
        if not self.check_cell_diff():
            judge = False
        
        # energy
        if not self.check_energy_diff():
            judge = False

        # print
        self.print_result(md, omp, mpi, judge)
