import math
import numpy as np
from .md_info import MDInfo

class TesterMethods:

    atoms_diff: dict[str, float]
    cell_diff: np.array[float]
    energy_diff: list[float]

    def __init__(self):
        pass

    def get_energy_from_out(self)->list[float]:
        """
        lax(laich) のoutfile から,
        エネルギー、温度を抜き取る 
        """
        pass

    def check_atoms_diff(self)->bool:
        """
        sf.atomsを比較する
        """
        for col in self.laich.atoms:
            self.atoms_diff[col] = 1e9
            diffs = (self.laich.atoms[col] - self.lax.atoms[col]).abs()
            self.atoms_diff[col] = [max(diff, self.atoms_diff[col]) for diff in diffs]

        atoms_judge = True
        for col, val in self.atoms_diff.items():
            if not col in self.config["allowable_error"]:
                continue
            if self.config["allowable_error"][col] < val:
                atoms_judge = False
        
        return atoms_judge

    def check_cell_diff(self)->bool:
        """
        sf.cellを比較する
        """
        self.cell_diff = np.abs(self.laich.cell - self.lax.cell)
        cell_judge = True
        if "cell" in self.config["allowable_error"]:
            for diff in self.cell_diff:
                if self.config["allowable_error"]["cell"] < diff:
                    cell_judge = False

        return cell_judge 
            


    def check_energy_diff(self)->bool:
        """
        エネルギーと温度を比較する
        """
        self.energy_diff = np.abs(self.laich_energy - self.lax_energy)
        energy_judge = True
        for diff, energy in zip(self.energy_diff, ["temp", "Kin_E", "Pot_E"]):
            if not energy in self.config["allowable_error"]:
                continue
            if self.config["allowable_error"][energy] < diff:
                energy_judge = False

        return energy_judge

    def print_result(self, md: MDInfo, judge: bool):
        """
        laichとlaxを比較した結果を出力する
        """
        pass