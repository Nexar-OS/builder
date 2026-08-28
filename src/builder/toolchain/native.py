from pathlib import Path
from .toolchain import Toolchain
from builder.build.machine import detect_machine
from builder.utils.logger import info

class NativeToolchain(Toolchain):
    """
    Representation of the build systems native compiler toolchain.
    """

    def __init__(self):
        host = detect_machine()
        info(f"Detected host architecture '{host.arch}'")

        super().__init__(
            name="native",
            target=host,
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