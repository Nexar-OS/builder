from dataclasses import dataclass
from enum import Enum

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
class Target(Enum):
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