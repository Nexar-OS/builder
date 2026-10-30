from pathlib import Path
from .toolchain import Toolchain
from builder.build.machine import detect_machine, nproc
from builder.utils.logger import info
from builder.build.environment import _native_tool

_NATIVE_TOOLCHAIN = None
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
            sysroot=Path("/"),
            num_jobs=nproc()
        )
    
    @classmethod
    def get(cls) -> "NativeToolchain":
        """Get a native toolchain.

        This method returns a native toolchain and keeps
        track of it.

        Returns:
            NativeToolchain: The toolchain.
        """
        global _NATIVE_TOOLCHAIN
        if not _NATIVE_TOOLCHAIN:
            _NATIVE_TOOLCHAIN = cls()

        return _NATIVE_TOOLCHAIN
    
    @property
    def cc(self) -> str:
        return _native_tool("gcc")
    
    @property
    def cxx(self) -> str:
        return _native_tool("g++")
    
    @property
    def ar(self) -> str:
        return _native_tool("ar")
    
    @property
    def as_(self) -> str:
        return _native_tool("as")
    
    @property
    def ld(self) -> str:
        return _native_tool("ld")
    
    @property
    def nm(self) -> str:
        return _native_tool("nm")
    
    @property
    def ranlib(self) -> str:
        return _native_tool("ranlib")
    
    @property
    def strip(self) -> str:
        return _native_tool("strip")