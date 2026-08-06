import os
import subprocess

from pathlib import Path

from build import BuildContext
from toolchain import Toolchain

from recipe.toolchain import *
from recipe.sysroot import *

from utils.logger import info, warn, debug
from utils.file import rmtree

def validate_toolchain(
        toolchain_dir: Path,
        sysroot: Path,
        triple: str) -> bool:
    """
    Validate an existing cross compiler toolchain.

    Checks:
        - Required compiler binaries exist.
        - Sysroot contains required directories.
        - GCC reports the expected target triple.
        - GCC reports the expected sysroot.
        - C++ compiler can execute

    Returns:
        bool: True if the cross compiler is valid.
    """

    info(f"Testing toolchain '{triple}' at '{str(toolchain_dir)}'")

    # Check compiler binaries exist
    for tool in [
        f"{triple}-gcc",
        f"{triple}-g++",
        f"{triple}-ld",
        f"{triple}-ar",
    ]:
        binary = toolchain_dir / "bin" / tool

        if not binary.is_file() or not os.access(binary, os.X_OK):
            debug(f" | Couldn't find binary: {binary}")
            return False

    # Check required sysroot paths exist
    for path in [
        sysroot / "usr" / "include",
        sysroot / "usr" / "lib"
    ]:
        if not path.exists():
            debug(f" | Couldn't find sysroot path: {path}")
            return False
    
    gcc = str(toolchain_dir / "bin" / f"{triple}-gcc")
    result = subprocess.run(
        [ gcc, "-dumpmachine" ],
        capture_output=True,
        text=True
    )

    # No access to gcc
    if result.returncode != 0:
        debug(" | GCC failed to execute.")
        return False
    
    # Mismatched triple
    reported_triple = result.stdout.strip()
    if reported_triple != triple:
        debug(f" | Triple mismatch: {reported_triple} != {triple}")
        return False

    # Verify GCC sysroot
    reported_sysroot = Path(
        subprocess.run(
            [ gcc, "--print-sysroot" ],
            capture_output=True,
            text=True
        ).stdout.strip()
    )

    if reported_sysroot != sysroot:
        debug(f" | Sysroot mismatch: {reported_sysroot} != {sysroot}")
        return False
    
    # Verify C++ frontend
    gxx = toolchain_dir / "bin" / f"{triple}-g++"

    result = subprocess.run(
        [ gxx, "--version" ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        debug(" | G++ failed to execute.")
        return False

    # All checks passed
    info(" | Toolchain OK.")
    return True
    
    

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
    is_valid = validate_toolchain(
        toolchain_dir=ctx.cross_toolchain_dir,
        sysroot=ctx.cross_toolchain_sysroot,
        triple=ctx.target_machine.triple
    )

    # Invalid toolchain was loaded
    if not is_valid:
        info("Tried to load invalid toolchain.")
        return None

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
    info(f"Building new cross compiler toolchain using {ctx}")

    info(f" | Cleaning environment...")
    rmtree(ctx.cross_toolchain_dir)
    rmtree(ctx.cross_toolchain_sysroot)

    ntc = ctx.toolchain

    info(f" | Bootstrapping cross compiler...")

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

    info(f" | Populating compiler sysroot...")
    LinuxHeadersRecipe().build(ctx)
    GlibCRecipe().build(ctx)

    # Now that the cross compiler sysroot contains Linux headers and glibc,
    # rebuild GCC using the native build compiler.
    #
    # GCC itself is always built by a compiler that runs on the build
    # machine, but the result is a compiler that runs on the build
    # machine and generates binaries for the target machine.
    ctx.toolchain = ntc
    info(f" | Completing compiler...")
    GCCSecondPassRecipe().build(ctx)

    # Construct the final cross compiler
    toolchain = Toolchain(
        name="cross",
        target=ctx.target_machine,
        prefix=ctx.cross_toolchain_dir,
        sysroot=ctx.cross_toolchain_sysroot
    )

    # Validate toolchain
    info("Testing new toolchain.")
    if not validate_toolchain(
        toolchain_dir=toolchain.prefix,
        sysroot=toolchain.sysroot,
        triple=toolchain.target.triple
    ):
        warn("Freshly build toolchain doesn't pass validation!")
        raise RuntimeError()

    return toolchain

def load_or_build_cross_toolchain(ctx: BuildContext):
    """
    Try to load an existing toolchain from an older run.
    If no toolchain exists, or the existing one is invalid,
    a new one will be build.

    Args:
        ctx (BuildContext): Context used for detecting and building the toolchain
    """

    toolchain = load_cross_toolchain(ctx)

    # Could load a toolchain
    if toolchain:
        return toolchain

    # Couldn't load an existing toolchain
    # Build a new one

    toolchain = build_cross_toolchain(ctx)

    return toolchain