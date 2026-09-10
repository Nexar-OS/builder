from pathlib import Path

from builder.toolchain import NativeToolchain, load_or_build_cross_toolchain
from builder.stage import Stage
from builder.build import (
    BuildContext,
    Target,
    detect_machine,
    detect_parallelism
)

from builder.recipe import *

max_workers, num_jobs = detect_parallelism()

ctx = BuildContext(
    registry                = RecipeRegistry([
                                    Path(__file__).parent.parent / "recipe",
                                    Path(__file__).parent.parent / "bundle",
                                ]),
    build_dir               = Path("build").resolve(),
    staging_dir             = Path("build/staging").resolve(),
    metadata_dir            = Path("build/.metadata").resolve(),
    build_machine           = detect_machine(),
    target_machine          = Target.X86_64,
    toolchain               = NativeToolchain(),
    toolchain_dir           = Path("build/toolchain/binaries").resolve(),
    toolchain_sysroot       = Path("build/toolchain/sysroot").resolve(),
    num_jobs                = num_jobs,
    verbose_build_logs      = False,
)

ctx.toolchain = load_or_build_cross_toolchain(ctx)

Stage.for_recipe(ctx, "core") \
    .build() \
    .export()