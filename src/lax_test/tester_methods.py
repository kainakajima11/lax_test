class TesterMethods:
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
        pass

    def check_cell_diff(self)->bool:
        """
        sf.cellを比較する
        """
        pass

    def check_energy_diff(self)->bool:
        """
        エネルギーと温度を比較する
        """
        pass

    def print_result(self):
        """
        laichとlaxを比較した結果を出力する
        """
        pass