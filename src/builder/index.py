from pathlib import Path

from builder.toolchain import NativeToolchain, load_or_build_cross_toolchain
from builder.stage import Stage
from builder.build import (
    BuildContext,
    Target,
    detect_machine,
    nproc
)

from builder.recipe import (
    RecipeRegistry,
    BuildRole,
    DependencyKind,
    DependencyGraph
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

ctx.toolchain = load_or_build_cross_toolchain(ctx)

registry = RecipeRegistry([
    Path(__file__).parent.parent / "recipe"
])

stage = Stage(
    ctx=ctx,
    registry=registry,
    name="test",
    recipes=[
        "bash-completion",
        "curl",
        "nano",
        "bc"
    ],
    add_runtime_dependencies=True
)


print(stage.sequencer.build())