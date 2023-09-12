from typing import Any
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

        # mdを実行していく
        for num, md in enumerate(md_list): # mdごとにtest実行
            # laich
            self.calculate_by_laich(md)

            #lax
            for omp, mpi in zip(self.config["OMPGrid"], self.config["MPIGrid"]):
                self.calculate_by_lax(md, omp, mpi)

                # 結果を比較
                self.compare_result()
    
    def check_and_set_config(self):
        """
        tester_configが必要な情報を含んでないかや、
        不適切な形式でないかcheckする。
        また入力がなかった部分にdefault値をsetする.
        """
        pass

    def get_md_list(self)->list[MDInfo]:
        """
        計算を実行するmdのリストを作成する.
        リストはMDに関する情報を持つMDInfoを要素とする.
        """
        pass

    def calculate_by_laich(self, md: MDInfo):
        """
        laichによってMDを実行する.
        計算後、構造がsfとしてself.laichに
        エネルギーや温度がlist[float]としてself.laich_energyに入る
        """
        self.laich = SimulationFrame(md.para)
        self.laich.laich(

        )
        self.laich_energy = self.get_energy_from_out()

    def calculate_by_lax(self, md: MDInfo, omp: int, mpi: int):
        """
        laxによってMDを実行する.
        計算後、構造がsfとしてself.laxに
        エネルギーや温度がlist[float]としてself.lax_energyに入る
        """
        self.lax = SimulationFrame(md.para)
        self.lax.lax(

        )
        self.lax_energy = self.get_energy_from_out()

    def compare_result(self):
        """
        self.laichとself.lax,
        self.laich_energyとself.lax_energyを比較する.
        """
        judge = True
        # sf.atoms 
        if self.check_atoms_diff():
            judge = False
        
        # sf.cell
        if self.check_cell_diff():
            judge = False
        
        # energy
        if self.check_energy_diff():
            judge = False

        self.print_result()