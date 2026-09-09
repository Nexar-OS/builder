from .context import BuildContext
from .version import Version
from .machine import (
    MachineSpec,
    Target,
    detect_triple,
    detect_machine,
    detect_ram,
    detect_parallelism,
    nproc,
)