from typing import Any
from copy import deepcopy
import pathlib
from limda import SimulationFrame
from .tester_methods import TesterMethods
from .md_info import MDInfo

class LaxTester(TesterMethods):
    config: dict[str, Any]
    lax: SimulationFrame
    lax_energy: list[float]
    laich: SimulationFrame
    laich_energy: list[float]

    def __init__(self, config: dict[str ,Any]):
        self.config: dict[str, Any] = config

    def run_lax_test(self):
        # testのconfigをcheck
        self.check_and_set_config(self.config)

        # 実行するmdのlistを作成
        md_list = self.get_md_list()

        # make dir
        self.config["laich_calc_dir"].mkdir()
        self.config["lax_calc_dir"].mkdir()

        # mdを実行、比較
        for md in md_list:
            # laich
            self.calculate_by_laich(md)

            #lax
            for omp, mpi in zip(self.config["OMPGrid"], self.config["MPIGrid"]):
                self.calculate_by_lax(md, omp, mpi)

                # 結果を比較
                self.compare_result(md)
    
    def check_and_set_config(self):
        """
        tester_configが必要な情報を含んでないかや、
        不適切な形式でないかcheckする。
        また入力がなかった部分にdefault値をsetする.
        """
        cf = self.config
        assert cf["mode"] == "own", "Inappropriate mode" #  or cf["mode"] == "testcase" or cf["mode"] == "random" # todo

        # own
        if cf["mode"] == "own":
            # check input_paths, input_names
            assert cf["input_paths"]
            if not cf["input_names"]:
                cf["input_names"] = [i for i, _ in enumerate(cf["input_paths"])]
            assert len(cf["input_paths"]) == len(cf["input_names"])

            # mask_info, mask_info_names
            if not cf["mask_info"]:
                cf["mask_info"] = [[]]
            if not cf["mask_info_names"]:
                cf["mask_info_names"] = [i for i, _ in enumerate(cf["mask_info"])]
            assert len(cf["mask_info"]) == len(cf["mask_info_names"])

            # omp, mpi
            if not cf["OMPGrid"]:
                cf["OMPGrid"] = [111]
            if not cf["MPIGrid"]:
                cf["MPIGrid"] = [111]
            
    
    def get_md_list(self)->list[MDInfo]:
        """
        計算を実行するmdのリストを作成する.
        リストはMDに関する情報を持つMDInfoを要素とする.
        """
        md_list = []
        for mask_info, mask_info_name in zip(self.config["mask_info"], self.config["mask_info_names"]):
            for i, input_path, input_name in enumerate(zip(self.config["input_paths"], self.config["input_names"])):
                md = MDInfo(self.config["para"][i],
                            input_path,
                            mask_info,
                            self.config["md_config"],
                            f"{input_name}_{mask_info_name}")
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
        laich_md = deepcopy(md)
        self.set_laich(laich_md)
        self.laich.laich(calc_dir = self.config["laich_calc_dir"] / laich_md.name,
                         laich_config = laich_md.config,
                         print_laich = True,
                         exist_ok = True,
                         laich_cmd = self.config["laich_dir"],
                         mask_info = laich_md.mask_info,
                         )
        # 結果からenergyを抜き取る
        self.laich_energy = self.get_energy_from_out()

    def calculate_by_lax(self, md: MDInfo, omp: int, mpi: int):
        """
        laxによってMDを実行する.
        計算後、構造がsfとしてself.laxに
        エネルギーや温度がlist[float]としてself.lax_energyに入る
        """
        self.lax = SimulationFrame()
        self.lax.import_para_from_list(md.para)
        self.set_lax(md, omp, mpi)
        self.lax.lax(calc_dir = self.config["lax_calc_dir"] / f"{md.name}_{mpi}_{mpi}",
                     lax_config = md.config,
                     print_lax = True,
                     exist_ok = True,
                     lax_cmd = self.config["lax_dir"],
                     mask_info = md.mask_info
                     )
        # 結果からenergyを抜き取る
        self.lax_energy = self.get_energy_from_out()

    def compare_result(self, md):
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
        self.print_result(md, judge)