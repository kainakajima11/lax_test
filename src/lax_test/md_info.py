from typing import Any

class MDInfo:
    para: list[str]
    input: str
    config: dict[str, Any]
    name: str

    def __init__(self):
        pass

    def config_to_laich(self)->dict[str, Any]:
        pass
    
    def config_to_lax(self)->dict[str, Any]:
        pass