import os
import shutil
import subprocess
import platform

from dataclasses import dataclass

from utils.logger import warn

@dataclass
class MachineSpec:
    """
    Describes a machine architecture.

    A ``MachineSpec`` groups the architecture identifiers required by the
    build system to construct a target triple and interact with the kernel-
    or toolchain-specific components.

    Attributes:
        arch (str): The userspace architecture name.
        kernel_arch (str): Architecture name expected by the kernel.
        triple (str): Full machine triple used by the toolchain.
    """

    arch: str
    kernel_arch: str
    triple: str

triple_suffix = "placeholder-linux-gnu"
class Target:
    """
    A collection of different target architectures.
    """
    X86_64 = MachineSpec(
        arch="x86_64",
        kernel_arch="x86_64",
        triple=f"x86_64-{triple_suffix}"
    )

    AARCH64 = MachineSpec(
        arch="aarch64",
        kernel_arch="aarch64",
        triple=f"aarch64-{triple_suffix}"
    )

    ARMV7 = MachineSpec(
        arch="armv7",
        kernel_arch="arm",
        triple=f"arm-{triple_suffix}"
    )



def detect_triple() -> str:
    """
    Detect the triple of the current host system

    Returns:
        str: The host triple
    """

    gcc = shutil.which("gcc")
    if gcc:
        return subprocess.check_output(
            [ gcc, "-dumpmachine" ],
            text=True
        ).strip()
    
    warn("Couldn't retrieve host triple from gcc. Falling back...")

    # Fallback if gcc is available
    arch = platform.machine().lower()
    return f"{arch}-linux-gnu"

def nproc() -> int:
    """
    Find the maximum num_jobs value
    """
    return os.cpu_count() or 1

def detect_machine() -> MachineSpec:
    """Detect the host machine architecture.

    Returns:
        MachineSpec: The host machine
    """

    assert platform.system().lower() == "linux", "Invalid host system!"

    # Get arch and normalize
    arch = platform.machine().lower()
    normalized = {
        "amd64": "x86_64",
        "arm64": "aarch64"
    }.get(arch, arch)

    kernel_arch_map = {
        "amd64": "x86_64",
        "aarch64": "arm64",
        "riscv64": "riscv",
    }

    return MachineSpec(
        arch=normalized,
        kernel_arch=kernel_arch_map.get(arch, arch),
        triple=detect_triple()
    )