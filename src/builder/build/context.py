import subprocess
from pathlib import Path
from dataclasses import dataclass, field

from threading import Lock

from .machine import MachineSpec

import typing
if typing.TYPE_CHECKING:
    from builder.recipe import RecipeRegistry, BuildRecipe
    from builder.toolchain.toolchain import Toolchain

from builder.utils.logger import global_logger

@dataclass
class BuildContext:
    """
    BuildContext serves as a global source of truth for several build variables.

    Attributes:
        registry (RecipeRegistry): The recipe registry to load recipes from.
        build_dir (Path): The directory where recipes will be build in.
        staging_dir (Path): The directory where the final output stages will be placed in.
        metadata_dir (Path): The directory where recipe metadata files will be stored.

        build_machine (MachineSpec): The "host-machine" on which the building will be executed.
        target_machine (MachineSpec): The targeted architecture the final build should run on.

        toolchain (Toolchain): Toolchain used to build the next recipe.
        toolchain_dir (Path): Directory where the (cross-)toolchain will be located.
        toolchain_sysroot (Path): Directory where the (cross-)toolchains sysroot will be located.

        num_jobs (int): The amount of concurrent build jobs.
        sysroot_lock (Lock): A global lock on recipes installing to sysroot.
        verbose_build_logs (bool): If ``True``, more detailed steps of build logs will be printed to ``stdout``.
    """
    registry: "RecipeRegistry"

    build_dir: Path
    staging_dir: Path
    metadata_dir: Path

    build_machine: MachineSpec
    target_machine: MachineSpec

    toolchain: "Toolchain"

    toolchain_dir: Path
    toolchain_sysroot: Path

    num_jobs: int

    sysroot_lock: Lock = field(default_factory=Lock)

    verbose_build_logs: bool = False

    @property
    def env(self) -> dict[str, str]:
        """
        Return the toolchains environment.
        """
        return self.toolchain.env or dict()

    def run(self,
            cmd: list[str],
            check: bool = True,
            use_toolchain_env: bool = True,
            use_fakeroot: bool = True,
            recipe: "BuildRecipe | None" = None,
            **kwargs
            ):
        """
        Execute a shell command sandboxed fakeroot and the build contexts environment.

        Args:
            cmd (list[str]): The command to invoke.
            check (bool, optional): Check for errors.
            use_toolchain_env (bool, optional): If set to False, no custom environment will be used.
            use_fakeroot (bool, optional): If set to False, no fakeroot will be used.
            recipe (BuildRecipe | None, optional): The build recipe which invoked this call.
        """

        logger = recipe.logger if recipe else global_logger

        logger.debug(f"> {' '.join(cmd)}")

        if use_toolchain_env:
            kwargs.setdefault("env", self.env)

        # Prepend fakeroot if enabled
        if use_fakeroot:
            cmd = [ "fakeroot" ] + cmd

        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            **kwargs
        )

        if check and result.returncode != 0:
            logger.error(
                f"Command failed: {' '.join(cmd)}\n\n"
                f"STDOUT: \n{result.stdout}\n\n\n"
                f"STDERR: \n{result.stderr}",
                exc_info=True,
                stack_info=True
            )
            raise
        
        return result