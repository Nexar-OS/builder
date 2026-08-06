from pathlib import Path
from .toolchain import Toolchain
from build.machine import detect_machine

class NativeToolchain(Toolchain):
    """
    Representation of the build systems native compiler toolchain.
    """

    def __init__(self):
        super().__init__(
            name="native",
            target=detect_machine(),
            prefix=Path("/usr"),
            sysroot=Path("/")
        )
    
    @property
    def cc(self) -> str:
        return "gcc"
    
    @property
    def cxx(self) -> str:
        return "g++"
    
    @property
    def ar(self) -> str:
        return "ar"
    
    @property
    def as_(self) -> str:
        return "as"
    
    @property
    def ld(self) -> str:
        return "ld"
    
    @property
    def nm(self) -> str:
        return "nm"
    
    @property
    def ranlib(self) -> str:
        return "ranlib"
    
    @property
    def strip(self) -> str:
        return "strip"