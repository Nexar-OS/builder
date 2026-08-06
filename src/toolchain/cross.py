from build import BuildContext
from toolchain import Toolchain

from recipe.toolchain import *
from recipe.sysroot import *

def load_cross_toolchain(ctx: BuildContext) -> Toolchain | None:
    """
    Load an existing cross compiler toolchain.

    Performs sanity checks to make sure the toolchain belongs to the requested
    target and that the sysroot contains the minimum required files.

    Args:
        ctx (BuildContext): Context to load the toolchain from

    Returns:
        Toolchain: The loaded cross compiler toolchain. None if toolchain is invalid.
    """
    # TODO: Implement toolchain validation

    return Toolchain(
        "cross",
        target=ctx.target_machine,
        prefix=ctx.cross_toolchain_dir,
        sysroot=ctx.cross_toolchain_sysroot
    )

def build_cross_toolchain(ctx: BuildContext) -> Toolchain:
    """
    Build a complete cross-compiler toolchain using a staged bootstrap process.

    The build happens in multiple phases because the final compiler cannot be
    built until the target system has its own C library headers and runtime.

    The resulting Toolchain object is the compiler used for building all future
    target packages and root filesystem artifacts.

    Args:
        ctx (BuildContext): Context passed to the recipes

    Returns:
        Toolchain: Cross compiler toolchain used for future compilations.
    """

    ntc = ctx.toolchain

    # Bootstrap with host compiler
    # No target compiler yet
    #
    # The first GCC pass only produces a minimal C compiler:
    # - no target C library yet
    # - no target headers exist yet
    BinutilsRecipe().build(ctx)
    GCCFirstPassRecipe().build(ctx)

    # Bootstrap compiler now exists, but it needs a target system
    # environment to finish the compiler build.
    #
    # At this stage the sysroot is still incomplete and is being
    # populated with the target Linux API and C library.
    ctx.toolchain = Toolchain(
        name="cross-bootstrap",
        target=ctx.target_machine,
        prefix=ctx.cross_toolchain_dir,
        sysroot=ctx.cross_toolchain_sysroot
    )

    LinuxHeadersRecipe().build(ctx)
    GlibCRecipe().build(ctx)

    # Now that the cross compiler sysroot contains Linux headers and glibc,
    # rebuild GCC using the native build compiler.
    #
    # GCC itself is always built by a compiler that runs on the build
    # machine, but the result is a compiler that runs on the build
    # machine and generates binaries for the target machine.
    ctx.toolchain = ntc
    GCCSecondPassRecipe().build(ctx)

    # Construct the final cross compiler
    toolchain = Toolchain(
        name="cross",
        target=ctx.target_machine,
        prefix=ctx.cross_toolchain_dir,
        sysroot=ctx.cross_toolchain_sysroot
    )

    return toolchain