from typing import Any, Union
import pathlib

class MDInfo:
    para: list[str]
    input_path: Union[str, pathlib.Path]
    config: dict[str, Any]
    mask_info: list[str]
    name: str

    def __init__(self,
                 para,
                 input_path,
                 mask_info,
                 name,
                 config,
                 input_id):
        self.para = para
        self.input_path = input_path
        self.mask_info = mask_info
        self.name = name
        self.config = {}
        self.set_config(config, input_id)         
    
    def set_config(self, config: dict[str, Any], id: int):
        for col, lst in config.items():
            if len(lst) == 1:
                self.config[col] = lst[0]
            else:
                self.config[col] = lst[id]

    def set_laich(self):
        # mask_info
        self.change_mask_info_for_laich()

        # mpi
        self.config["MPIGridX"] = 1
        self.config["MPIGridY"] = 1
        self.config["MPIGridZ"] = 1
        
        # omp
        self.config["OMPGridX"] = 1
        self.config["OMPGridY"] = 1
        self.config["OMPGridZ"] = 1

    def change_mask_info_for_laich(self):
        if not self.mask_info:
            return

        new_mask_info = []
        for i, info in enumerate(self.mask_info):
            splitted_info = info.split()
            if splitted_info[0] == "#move":
                new_mask_info = self.laich_move_info(splitted_info ,new_mask_info)
            elif splitted_info[0] == "#pressz":
                new_mask_info = self.laich_press_info(splitted_info, new_mask_info)
        self.mask_info = new_mask_info
    
    def laich_move_info(self, spinfo: list[str], new_mask_info: list[str]):
        if spinfo[2] == "x":
            if float(spinfo[3]) == 0.0:
                new_mask_info.append(f"#fix {spinfo[1]} rigid {spinfo[2]} - -")
                spinfo[2] = "-"
                spinfo[3] = "-"
        if spinfo[4] == "y":
            if float(spinfo[5]) == 0.0:
                new_mask_info.append(f"#fix {spinfo[1]} rigid - {spinfo[4]} -")
                spinfo[4] = "-"
                spinfo[5] = "-"
        if spinfo[6] == "z":
            if float(spinfo[7]) == 0.0:
                new_mask_info.append(f"#fix {spinfo[1]} rigid - - {spinfo[6]}")
                spinfo[6] = "-"
                spinfo[7] = "-"
        if spinfo[2] == "x" or spinfo[4] == "y" or spinfo[6] == "z":
            spinfo.insert(2, "rigid")
            new_mask_info.append(" ".join(spinfo))
        return new_mask_info
    
    def laich_press_info(self, spinfo: list[str], new_mask_info: list[str]):
        spinfo[0] = "#press"
        spinfo.insert(2, "z")
        new_mask_info.append(" ".join(spinfo))
        return new_mask_info
        

    def set_lax(self, omp: int, mpi: int):
        # omp
        self.config["OMPGridX"] = omp // 100
        self.config["OMPGridY"] = (omp % 100) // 10
        self.config["OMPGridZ"] = omp % 10

        # mpi
        self.config["MPIGridX"] = mpi // 100
        self.config["MPIGridY"] = (mpi % 100) // 10
        self.config["MPIGridZ"] = mpi % 10
