import os
from pathlib import Path
from abc import ABC
from dataclasses import dataclass

from build.machine import MachineSpec

@dataclass
class Toolchain(ABC):
    """Representation of a toolchain and its build environment.

    A :class:`Toolchain` describes the location of a compiler toolchain targeting
    a specific :class:`~build.machine.MachineSpec`. It provides access to the standard
    GNU binutils and compiler executables, common build-system tools and a shell environment.

    Attributes:
        name (str): Human-readable name of the toolchain.
        target (MachineSpec): The target machine specification.
        prefix (Path): Installation prefix of the toolchain.
        sysroot (Path): Root directory representing the target system image, like headers or libraries.
    """

    name: str
    target: MachineSpec
    prefix: Path
    sysroot: Path

    @property
    def cc(self) -> str:
        return str(self.prefix / "bin" / f"{self.target.triple}-gcc")
    
    @property
    def cxx(self) -> str:
        return str(self.prefix / "bin" / f"{self.target.triple}-g++")
    
    @property
    def ar(self) -> str:
        return str(self.prefix / "bin" / f"{self.target.triple}-ar")
    
    @property
    def as_(self) -> str:
        return str(self.prefix / "bin" / f"{self.target.triple}-as")
    
    @property
    def ld(self) -> str:
        return str(self.prefix / "bin" / f"{self.target.triple}-ld")
    
    @property
    def nm(self) -> str:
        return str(self.prefix / "bin" / f"{self.target.triple}-nm")
    
    @property
    def ranlib(self) -> str:
        return str(self.prefix / "bin" / f"{self.target.triple}-ranlib")
    
    @property
    def strip(self) -> str:
        return str(self.prefix / "bin" / f"{self.target.triple}-strip")
    
    @property
    def make(self) -> str:
        return "make"
    
    @property
    def cmake(self) -> str:
        return "cmake"
    
    @property
    def meson(self) -> str:
        return "meson"
    
    @property
    def ninja(self) -> str:
        return "ninja"
    
    @property
    def pkg_config(self) -> str:
        return "pkg-config"
    
    @property
    def cflags(self) -> list[str]:
        return [
            "-O2",
            "-pipe",
            f"--sysroot={self.sysroot}",
            f"-I{self.sysroot}/usr/include",
        ]
    
    @property
    def ldflags(self) -> list[str]:
        return [
            "-Wl,-z,relro",
            "-Wl,-z,now",
            f"--sysroot={self.sysroot}",
            f"-L{self.sysroot}/usr/lib",
            f"-L{self.prefix / self.target.triple}/lib"
        ]
    
    @property
    def path(self) -> str:
        return str(self.prefix / "bin")
    
    @property
    def env(self) -> dict[str, str]:
        """Build a map of environment variables for a shell-sandbox.

        Returns:
            dict[str, str]: A map of all important environment variables.
        """
        return {
            **os.environ,
            "PATH": f"{self.path}:{os.environ.get('PATH', '')}",
            "CC": self.cc,
            "CXX": self.cxx,
            "AR": self.ar,
            "AS": self.as_,
            "LD": self.ld,
            "NM": self.nm,
            "RANLIB": self.ranlib,
            "STRIP": self.strip,
            "SYSROOT": str(self.sysroot),
            
            "CFLAGS": " ".join(self.cflags),
            "CPPFLAGS": " ".join(self.cflags),
            "CXXFLAGS": " ".join(self.cflags),
            "LDFLAGS": " ".join(self.ldflags),

            "PKG_CONFIG": self.pkg_config,
            "PKG_CONFIG_SYSROOT_DIR": f"{self.sysroot}",
            "PKG_CONFIG_LIBDIR": ":".join([
                str(self.sysroot / "usr/lib/pkgconfig"),
                str(self.sysroot / "usr/share/pkgconfig")
            ]),
        }