from pathlib import Path
from dataclasses import dataclass

from .machine import MachineSpec
from toolchain.toolchain import Toolchain

@dataclass
class BuildContext:
    """
    BuildContext serves as a global source of truth for several build variables.

    Attributes:
        build_dir (Path): The directory where recipes will be build in.
        
        build_machine (MachineSpec): The "host-machine" on which the building will be executed.
        target_machine (MachineSpec): The targeted architecture the final build should run on.

        toolchain (Toolchain): Toolchain used to build the next recipe.
        cross_toolchain_dir (Path): Directory where the cross toolchain will be located.
        cross_toolchain_sysroot (Path): Directory where the cross toolchains sysroot will be located.

        num_jobs (int): The amount of concurrent build jobs.
    """
    build_dir: Path

    build_machine: MachineSpec
    target_machine: MachineSpec

    toolchain: Toolchain

    cross_toolchain_dir: Path
    cross_toolchain_sysroot: Path

    num_jobs: int