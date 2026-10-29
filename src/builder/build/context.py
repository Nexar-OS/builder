import subprocess
from pathlib import Path
from dataclasses import dataclass

from .machine import MachineSpec

from functools import cached_property
import typing
if typing.TYPE_CHECKING:
    from builder.recipe import RecipeRegistry, BuildRecipe
    from builder.toolchain.toolchain import Toolchain
    from builder.recipe.identity import IdentityRegistry

from builder.utils.logger import global_logger


def _identity_registry(dir: Path) -> "IdentityRegistry":
    from builder.recipe.identity import IdentityRegistry
    return IdentityRegistry(dir)

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
        toolchain_host_tools (Path): Directory where HOST-recipes will be built into.

        num_jobs (int): The amount of concurrent build jobs.
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
    toolchain_host_tools: Path

    num_jobs: int

    verbose_build_logs: bool = False

    @property
    def env(self) -> dict[str, str]:
        """
        Return the toolchains environment.
        """
        return self.toolchain.env or dict()


    @cached_property
    def build_registry(self) -> "IdentityRegistry":
        return _identity_registry(self.metadata_dir)

    @cached_property
    def sysroot_registry(self) -> "IdentityRegistry":
        return _identity_registry(self.toolchain_sysroot / "packages")
    
    @cached_property
    def host_tools_registry(self) -> "IdentityRegistry":
        return _identity_registry(self.toolchain_host_tools / "packages")