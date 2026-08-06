from pathlib import Path

from toolchain import NativeToolchain, load_or_build_cross_toolchain
from build import (
    BuildContext,
    Target,
    detect_machine,
    nproc
)

ctx = BuildContext(
    Path("build").resolve(),
    build_machine=detect_machine(),
    target_machine=Target.X86_64,

    toolchain=NativeToolchain(),
    cross_toolchain_dir=Path("env/binaries").resolve(),
    cross_toolchain_sysroot=Path("env/sysroot").resolve(),

    num_jobs=nproc()
)

ctx.toolchain = load_or_build_cross_toolchain(ctx)