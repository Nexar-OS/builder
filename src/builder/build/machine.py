import os
import shutil
import subprocess
import platform
import math

from dataclasses import dataclass

from builder.utils.logger import warn

KERNEL_IMAGES = {
    "x86": ("arch/x86/boot/bzImage", "vmlinuz"),
    "arm64": ("arch/arm64/boot/Image", "Image"),
    "arm": ("arch/arm/boot/Image", "zImage"),
    "riscv": ("arch/riscv/boot/Image", "Image"),
}

@dataclass(frozen=True)
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

    @property
    def kernel_image(self) -> tuple[str, str]:
        image = KERNEL_IMAGES.get(self.kernel_arch)
        if not image:
            raise RuntimeError(f"Unrecognized kernel arch: '{self.kernel_arch}'")

        return image

    @property
    def libdir(self) -> str:
        """
        Returns the default library directory for the architecture
        """

        if self.arch in { "x86_64", "aarch64", "ppc64le", "s390x" }:
            return "usr/lib64"
        
        return "usr/lib"

triple_suffix = "placeholder-linux-gnu"
class Target:
    """
    A collection of different target architectures.
    """
    X86_64 = MachineSpec(
        arch="x86_64",
        kernel_arch="x86", # _64 will be determined by cross compiler
        triple=f"x86_64-{triple_suffix}"
    )

    AARCH64 = MachineSpec(
        arch="aarch64",
        kernel_arch="arm64",
        triple=f"aarch64-{triple_suffix}"
    )

    ARMV7 = MachineSpec(
        arch="armv7",
        kernel_arch="arm",
        triple=f"armv7-{triple_suffix}eabihf"
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

def detect_ram() -> float:
    """
    Reads MemTotal from /proc/meminfo.

    Returns:
        float: Returns the amount of ram of this machine (in GiB).
    """
    with open("/proc/meminfo", "r") as f:
        for line in f:
            if line.startswith("MemTotal:"):
                kib = int(line.split()[1])
                return kib / (1024 ** 2)
    
    raise RuntimeError("Unable to determine system ram.")

def detect_parallelism(cores: int | None = None, ram: float | None = None, ram_per_recipe: int = 8) -> tuple[int, int]:
    """Determine suitable build parallelism for the current system.
    
    The calculation aims to keep CPU at high utilization while limiting
    the number of simultaneously active recipes to avoid memory and filesystem
    contention.

    Args:
        cores (int | None): The amount of cores of the machine (defaults to whatever ``nproc`` returns).
        ram (int | None): The amount of ram (in GiB) (defaults to whatever ``/proc/meminfo`` returns).
        ram_per_recipe (int): A general assumption of how much ram each recipe will consume.

    Returns:
        tuple[int, int]: (max_workers, num_jobs)
    """
    cores = cores or nproc()
    ram = ram or detect_ram()

    # Prefer several independent recipes on larger machines
    if cores <= 4:
        max_workers = 1
    elif cores <= 8:
        max_workers = 2
    elif cores <= 16:
        max_workers = 3
    elif cores <= 32:
        max_workers = 4
    else:
        max_workers = 8

    # Reduce concurrency on memory-constrained systems
    max_workers = min(
        max_workers,
        max(1, math.floor(ram / ram_per_recipe))
    )

    # Slightly oversubscribe the CPU so that jobs waiting on I/O
    # operations don't leave cores idle.
    total_jobs = math.ceil(cores * 1.5)

    # Divide available CPU parallelism between recipes
    num_jobs = max(1, math.ceil(total_jobs / max_workers))

    return max_workers, num_jobs