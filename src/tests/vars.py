from pathlib import Path
from builder.toolchain import NativeToolchain
from builder.build import (
    BuildContext,
    detect_machine,
    nproc,
    Target
)

ctx = BuildContext(
    build_dir               = Path("build").resolve(),
    staging_dir             = Path("build/staging").resolve(),
    metadata_dir            = Path("build/.metadata").resolve(),
    build_machine           = detect_machine(),
    target_machine          = Target.X86_64,
    toolchain               = NativeToolchain(),
    cross_toolchain_dir     = Path("build/toolchain/binaries").resolve(),
    cross_toolchain_sysroot = Path("build/toolchain/sysroot").resolve(),
    num_jobs                = nproc()
)