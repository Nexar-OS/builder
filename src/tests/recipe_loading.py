from pathlib import Path
from builder.recipe.loader import *
from builder.recipe import BuildRole
from builder.toolchain import (
    NativeToolchain,
    load_or_build_cross_toolchain
)
from builder.build import (
    BuildContext,
    detect_machine,
    nproc,
    Target
)

recipe_dir = Path("src/recipe")

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

def recipe(name: str, role: BuildRole|None = None):
    recipe = load_recipe(recipe_dir / f"{name}.yaml", role or BuildRole.TARGET, ctx)

    if not recipe:
        raise RuntimeError(f"Failed to load recipe: '{name}'")

    return recipe

recipe("glib") \
    .build()