from typing import Any

class MDInfo:
    para: list[str]
    input_path: str
    config: dict[str, Any]
    mask_info: list[str]
    name: str

    def __init__(self,
                 para,
                 input_path,
                 mask_info,
                 config,
                 name):
        self.para = para
        self.input_path = input_path
        self.mask_info = mask_info
        self.config = config
        self.name = name
        

    def set_laich(self)->dict[str, Any]:
        pass
    
    def set_lax(self)->dict[str, Any]:
        pass