import numpy as np
from typing import Union, Any
import pathlib
from limda import SimulationFrame
from .md_info import MDInfo

class TesterMethods:

    def __init__(self):
        pass

    def set_initial_velocity(self, md):
        sf = SimulationFrame()
        sf.import_para_from_list(md.para)
        sf.import_input(md.input_path)
        md.set_lax(111)
        cf = md.config.copy()
        cf["TotalStep"] = 0
        cf["ReadVelocity"] = 0
        sf.lax(
            calc_dir = self.config["calc_dir"] / "initial_velo" / f"{md.name}",
            lax_config = cf,
            print_lax = True,
            exist_ok = True,
            lax_cmd = self.config["lax_cmd"],
        )
        md.input_path = self.config["calc_dir"] / "initial_velo" / f"{md.name}" / "dump.pos.0" 

    def get_energy_from_out(self, ofp: Union[str, pathlib.Path], md: MDInfo)->list[float]:
        """
        lax(laich) のoutfile から,
        エネルギー、温度を抜き取る 
        """
        with open(ofp, "r") as f:
            lines = f.readlines()
            for line in lines:
                spline = line.split()
                if len(spline) == 0:
                    continue
                if spline[0] == str(md.config["TotalStep"]):
                    energies = np.array([float(spline[i+1]) for i in range(4)])
                    break
        return energies

    def check_atoms_diff(self)->bool:
        """
        sf.atomsを比較する
        """
        self.atoms_diff = {}
        for col in ["x", "y", "z", "vx", "vy", "vz"]:
            self.atoms_diff[col] = 0
            diffs = (self.laich.atoms[col] - self.lax.atoms[col]).abs()
            for diff in diffs:
                self.atoms_diff[col] = max(diff, self.atoms_diff[col])

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
        for diff, energy in zip(self.energy_diff, ["temp", "Kin_E", "Pot_E", "Total_E"]):
            if not energy in self.config["allowable_error"]:
                continue
            if self.config["allowable_error"][energy] < diff:
                energy_judge = False

        return energy_judge

    def print_result(self, md: MDInfo, omp: int, mpi: int, judge: bool):
        """
        laichとlaxを比較した結果を出力する
        """
        if judge:
            pass_comment = f"Pass : {md.name}, OMP : {omp}, MPI : {mpi}"
            self.result_comments_list.append(pass_comment)
            print(pass_comment, flush=True)
        else:
            error_comment = f"Error : {md.name}, OMP : {omp}, MPI : {mpi}\n" \
                        + "---------------------------------------\n" \
                        + f"X                : {self.atoms_diff['x']}\n" \
                        + f"Y                : {self.atoms_diff['y']}\n" \
                        + f"Z                : {self.atoms_diff['z']}\n" \
                        + f"V_X              : {self.atoms_diff['vx']}\n" \
                        + f"V_Y              : {self.atoms_diff['vy']}\n" \
                        + f"V_Z              : {self.atoms_diff['vz']}\n" \
                        + f"Cell             : {self.cell_diff}\n" \
                        + f"Temperature      : {self.energy_diff[0]}\n" \
                        + f"Kinetic_energy   : {self.energy_diff[1]}\n" \
                        + f"Potential_energy : {self.energy_diff[2]}\n" \
                        + f"Total_energy     : {self.energy_diff[3]}\n" \
                        + "---------------------------------------\n"
            self.result_comments_list.append(error_comment)
            print(error_comment, flush=True)

    def print_all_results(self):
        print("\n\n-- Lax Test Results ---\n\n")
        for comment in self.result_comments_list:
            print(comment, flush=True)
