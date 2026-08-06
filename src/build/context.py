from pathlib import Path
from dataclasses import dataclass

from .machine import MachineSpec

@dataclass
class BuildContext:
    """
    BuildContext serves as a global source of truth for several build variables.

    Attributes:
        build_dir (Path): The directory where recipes will be build in.
        
        build_machine (MachineSpec): The "host-machine" on which the building will be executed.
        target_machine (MachineSpec): The targeted architecture the final build should run on.

        num_jobs (int): The amount of concurrent build jobs.
    """
    build_dir: Path

    build_machine: MachineSpec
    target_machine: MachineSpec

    num_jobs: int