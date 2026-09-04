from __future__ import annotations
from typing import TYPE_CHECKING

from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum, StrEnum, auto

import time
import json
from hashlib import sha256

from builder.source.source import Source
from builder.build.context import BuildContext

if TYPE_CHECKING:
    from builder.build.system import BuildSystem

from builder.utils.logger import info, warn
from builder.utils.file import rmtree, merge_trees
from .dependencies import Dependencies

@dataclass(frozen=True)
class RecipeMetadata:
    """
    A ``RecipeMetadata`` stores build specific metadata for the builder to
    decide if a rebuild is necessary.
    """

    name: str
    fingerprint: str
    last_build: str

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "RecipeMetadata":
        """Create metadata from a dictionary."""
        return cls(
            name=data["name"],
            fingerprint=data["fingerprint"],
            last_build=data["last_build"]
        )

    @classmethod
    def load(cls, path: Path):
        """Load a recipe's metadata from a savefile.

        Returns:
            "RecipeMetadata"|None: Returns None if passes file isn't a metadata file.
                                   Otherwise the metadata object will be returned.
        """
        if not path.is_file():
            return None
        
        return cls.from_dict(
            json.loads(path.read_text())
        )

class BuildMethod(StrEnum):
    """
    Describes where the source and build tree should be located.
    """

    IN_SOURCE = "IN_SOURCE"
    """
    Build will run inside of the source-tree.
    """

    OUT_OF_SOURCE = "OUT_OF_SOURCE"
    """
    Build will run in a separate directory than the source-tree.
    """

class BuildRole(Enum):
    """
    Describes where the output of a recipe is intended to be used.

    Build roles distinguish recipes that run on the build machne
    from those that belong onto the target os.
    """

    TOOLCHAIN = auto()
    """
    Component of the (cross-)compilation toolchain and added to path.

    These components are used by the builder to produce
    target binaries.
    """

    SYSROOT = auto()
    """
    Target development component installed into the (cross-)toolchain.

    This includes target headers, libraries, ld files, etc.
    """

    TARGET = auto()
    """
    Runtime component installed into the target filesystem.

    These files become part of the final os.
    """

class BuildRecipe(ABC):
    """
    Abstract base class describing how a software package is built.

    A ``BuildRecipe`` encapsulates all information required to fetch sources,
    configure a build system, compile a project, and install the resulting
    artifacts into a destination directory.

    Attributes:
        name (str): Human-readable name of the package or component.
        version (str): Version string of the package being built.
        recipe_type (RecipeType): The type of recipe being built.
        sources (list[Source]): Collection of :class:`Source` objects required for the build.
        build_system (BuildSystem): Build system implementation responsible for configuring,
                                    compiling, and installing the package.
    """
    def __init__(self, ctx: BuildContext, role: BuildRole) -> None:
        super().__init__()

        self.build_role = role
        self.ctx = ctx

    dependencies: Dependencies = Dependencies.none()

    name: str
    version: str

    sources: list[Source]

    build_method: BuildMethod = BuildMethod.OUT_OF_SOURCE  # most recipes are build out-of-source
    
    build_system: BuildSystem|None = None

    @property
    def fingerprint(self) -> str:
        """
        Compute a deterministic fingerprint for this recipe.

        The fingerprint uniquely identifies the current build state of the
        recipe by hashing:
        - the recipe name
        - the resolved build options

        Returns:
            str: A SHA-256 digest representing the recipe state.
        """
        h = sha256()

        # Recipe identity
        h.update(self.name.encode())
        h.update(str(self._dest_dir or "").encode())

        # h.update(str(self.ctx).encode()) # doesn't work because of ctx.registry
        h.update(str(self.ctx.build_dir).encode())
        h.update(str(self.ctx.build_machine.triple).encode())
        h.update(str(self.ctx.target_machine.triple).encode())
        h.update(str(self.ctx.toolchain_dir).encode())
        h.update(str(self.ctx.toolchain_sysroot).encode())

        # Build system args
        config_args = self._config_args(self.ctx)
        build_args = None
        install_args = None
        if self.build_system:
            if self.build_system.config_args:
                config_args = config_args + self.build_system.config_args

            build_args = self.build_system.build_args
            install_args = self.build_system.install_args

        h.update(f"{config_args}-{build_args}-{install_args}".encode())

        return h.hexdigest()

    @property
    def metadata_path(self) -> Path:
        """
        Return the path to the recipe's build metadata file.

        Returns:
            Path: Path to the JSON metadata file for this recipe.
        """
        path = self.ctx.metadata_dir / "recipes" / f"{self.name}.json"
        path.parent.mkdir(exist_ok=True, parents=True)

        return path

    @property
    def needs_rebuild(self) -> bool:
        """
        Determine whether the recipe must be rebuilt.

        A rebuild is required if no metadata from a previous build exists or 
        if the stored fingerprint differs from the fingerprint computed from
        the current recipe state.

        Returns:
            bool: True if the recipe should be rebuilt, otherwise False.
        """
        path = self.metadata_path

        if not path.exists():
            return True
        
        old = json.loads(path.read_text())["fingerprint"]
        return old != self.fingerprint

    def mark_built(self) -> None:
        """
        Record the current recipe fingerprint as successfully built.
        """
        path = self.metadata_path
        path.write_text(
            json.dumps(
                asdict(RecipeMetadata(
                    name=self.name,
                    fingerprint=self.fingerprint,
                    last_build=str(time.time())
                ))
            )
        )

    def _resolve_sources(self, source_dir: Path, build_dir: Path):
        """
        Resolve and install all configured sources into the working source directory.

        Args:
            source_dir (Path): The source directory for sources to be put into.
            build_dir (Path): The build directory.
        """
        
        for source in self.sources:
            dest_dir = None

            # If recipe is build in-source, we install the
            # source into the build directory directly
            if self.build_method == BuildMethod.IN_SOURCE:
                dest_dir = build_dir

            # If recipe is build out-of-source, we
            # install the source into the source directory
            elif self.build_method == BuildMethod.OUT_OF_SOURCE:
                dest_dir = source_dir

            source.install(source_dir, dest_dir)

    @property
    def work_dir(self) -> Path:
        """
        Create and return the working directory for this recipe.

        The working directory is derived from ``ctx.build_dir`` and the recipe name and version.

        Args:
            ctx (BuildContext): Context used for the build.

        Returns:
            Path: Absolute path where the build takes place
        """
        work_dir = self.ctx.build_dir / "recipe" / (self.name + "-" + self.version)
        work_dir.mkdir(exist_ok=True, parents=True)

        return work_dir.resolve()

    @property
    def _dest_dir(self) -> Path|None:
        """
        Return the directory where the build should be installed.

        Path is determined by the build role, this recipe was constructed with:

        ``BuildRole.TOOLCHAIN``: None (toolchain components use '--prefix')
        ``BuildRole.SYSROOT``: $ctx.cross_toolchain_sysroot
        ``BuildRole.TARGET``: $work_dir/rootfs

        Args:
            ctx (BuildContext): Context used for the build.

        Returns:
            Path: The path for the final build to be installed into.
        """
        dir = None
        match self.build_role:
            case BuildRole.TOOLCHAIN:
                dir = None

            case BuildRole.SYSROOT | BuildRole.TARGET:
                dir = self.work_dir / "rootfs"

            case _:
                raise NotImplementedError(
                    f"Build role not supported: '{self.build_role}'"
                )
        
        if dir:
            dir.mkdir(exist_ok=True, parents=True)

        return dir

    def _config_args(self, ctx: BuildContext) -> list[str]:
        """
        Generate build-system configuration arguments for this recipe.

        Args:
            ctx (BuildContext): Build context.

        Returns:
            list[str]: List of configuration args passed to the build system.
        """
        return []

    def _install_to_sysroot(self, delete_after_copy: bool = False):
        """
        Copies the build output into sysroot.

        No checks of the recipe built actually being
        ``BuildRole.SYSROOT`` are performed.

        Args:
            delete_after_copy (bool): If ``True``, deletes the rootfs.
        """

        source = self._dest_dir

        if not source:
            return

        if not source.is_dir():
            return

        merge_trees(
            source=source,
            dest=self.ctx.toolchain_sysroot,
            copy=not delete_after_copy,
            skip_extensions=[
                "la"
            ]
        )

    def build(self, force_rebuild: bool = False) -> None:
        """
        Executes the complete build lifecycle of the recipe.

        The build process follows this order:
        1. Create working, build, source, and destination directories
        2. Resolve and install all configured sources into the source directory.
        3. Run the optional :meth:`prepare` hook.
        4. Run the optional :meth:`patch` hook.
        5. Invoke the configured :class:`BuildSystem`.
        6. Run the optional :meth:`post_install` hook.

        Args:
            force_rebuild (bool): If ``True``, the self.needs_rebuild flag is ignored and the recipe is built again.
        """

        work_dir = self.work_dir
        build_dir = work_dir / "build"
        source_dir = work_dir / "sources"
        dest_dir = self._dest_dir

        build: bool = self.needs_rebuild or force_rebuild

        if build:
            info(f"Building recipe '{self.name}'...")

            # Ensure a fresh empty build directory
            if build_dir.is_dir():
                rmtree(build_dir)

            # Clean target root
            if (
                dest_dir
                and dest_dir.is_dir()
            ):
                rmtree(dest_dir)

            build_dir.mkdir(exist_ok=True, parents=True)
            source_dir.mkdir(exist_ok=True, parents=True)

            info(f"Building recipe '{self.name}-{self.version}' using \n{work_dir=}\n{build_dir=}\n{source_dir=}\n{dest_dir=}")

            self._resolve_sources(source_dir, build_dir)

            # Fix source directory passed to build system
            if self.build_method == BuildMethod.IN_SOURCE:
                source_dir = build_dir

            # Let recipes prepare their environment
            self.prepare(self.ctx, source_dir, build_dir)

            # Let recipes apply custom patches
            self.patch(self.ctx, source_dir)

            # Run installation
            if self.build_system:
                self.build_system.prepare(self, source_dir, build_dir, dest_dir)
                self.build_system.configure(self, source_dir, build_dir, dest_dir, self._config_args(self.ctx))
                self.build_system.build(self, source_dir, build_dir, dest_dir)
                self.build_system.install(self, source_dir, build_dir, dest_dir)
        
        else:
            info(f"Skipping build for recipe '{self.name}' (Up to date).")

        # Install to sysroot
        # This must run even when the recipe is already marked as built
        if self.build_role == BuildRole.SYSROOT:
            self._install_to_sysroot()

        if build:
            # Run post install hook
            self.post_install(self.ctx, dest_dir)

            self.mark_built()

    def patch(self, ctx: BuildContext, source_dir: Path) -> None:
        """
        Apply recipe-specific modifications to the resolved sources.

        This hook is called after all sources have been installed
        into the source directory, but before the configuration step.

        Args:
            ctx (BuildContext): Context used for current build.
            source_dir (Path): The directory to where the source was installed into.
        """
        ...

    def prepare(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        """
        Prepare the build environment before configuration begin.

        This hook is invoked after sources have been resolved but before any
        build-system preparation or configuration occurs.

        Args:
            ctx (BuildContext): Context used for current build.
            source_dir (Path): The directory to where the source was installed into.
            build_dir (Path): Directory where the recipe will be build in.
        """
        ...

    def post_install(self, ctx: BuildContext, dest_dir: Path|None) -> None:
        """
        Perform additional actions after the installation step has been completed.

        This hook is called at the very end of the build process.

        Args:
            ctx (BuildContext): Context used for current build.
            dest_dir (Path): The directory to where the program was built into.
        """
        ...
    
    def __repr__(self) -> str:
        return f"{self.name}-{self.version} ({self.build_role.name.upper()})"

@dataclass
class GenericRecipe(BuildRecipe):
    """
    Class for constructing a generic recipe just from arguments passed to it.

    A ``GenericRecipe`` provides an interface to create a full ``BuildRecipe`` 
    on the fly.

    See Also:
        :class:`BuildRecipe`: Base interface implementing core recipe workflow
    """

    def __init__(self,
                 ctx: BuildContext,
                 role: BuildRole,
                 name: str,
                 version: str,
                 sources: list[Source],
                 dependencies: Dependencies|None = None,
                 build_method: BuildMethod = BuildMethod.OUT_OF_SOURCE,
                 build_system: BuildSystem|None = None,
                 patches: list[Path]|None = None,
                 prepare_script: str|None = None,
                 post_install_script: str|None = None,
                 ) -> None:
        super().__init__(ctx, role)

        self.name = name
        self.version = version
        self.sources = sources
        self.dependencies = dependencies or Dependencies.none()
        self.build_method = build_method
        self.build_system = build_system
        self.patches = patches or []
        self.prepare_script = prepare_script
        self.post_install_script = post_install_script

    def patch(self, ctx: BuildContext, source_dir: Path) -> None:
        """
        Apply recipe-specific modifications to the resolved sources.

        This hook applies the patch files passed under ``patches``.

        Args:
            ctx (BuildContext): Context used for current build.
            source_dir (Path): The directory to where the source was installed into.
        """
        for patch in self.patches:
            info(f"Applying patch '{patch}' to recipe '{self.name}'")

            ctx.run(
                [
                    "patch",
                    "-p0",
                    "--input",
                    str(patch)
                ],
                cwd=source_dir,
                check=True
            )

    @property
    def env(self) -> dict[str, str]:
        return {
            "NAME": self.name,
            "VERSION": self.version
        }

    def prepare(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        """
        Prepare the build environment before configuration begin.

        This hook runs the script passed under ``prepare_script`` inside
        of a sandboxed shell environment.

        Args:
            ctx (BuildContext): Context used for current build.
            source_dir (Path): The directory to where the source was installed into.
            build_dir (Path): Directory where the recipe will be build in.
        """
        if not self.prepare_script:
            info(f"No prepare install script for {self.name}.")
            return

        ctx.run(
            [
                "sh", "-c", self.prepare_script
            ],
            cwd=build_dir,
            env={
                **ctx.env,
                **self.env,
                "SOURCE": str(source_dir),
                "BUILD": str(build_dir),
            }
        )
    
    def post_install(self, ctx: BuildContext, dest_dir: Path|None) -> None:
        """
        Perform additional actions after the installation step has been completed.

        This hook runs the script passed under ``post_install_script`` inside
        of a sandboxed shell environment.

        Args:
            ctx (BuildContext): Context used for current build.
            dest_dir (Path): The directory to where the program was built into.
        """
        if not self.post_install_script:
            info(f"No post install script for {self.name}.")
            return

        ctx.run(
            [
                "sh", "-c", self.post_install_script
            ],
            cwd=dest_dir,
            env={
                **ctx.env,
                **self.env,
                "DESTDIR": str(dest_dir)
            }
        )

    def __repr__(self) -> str:
        return super().__repr__()
    
class ToolchainRecipe(BuildRecipe):
    """
    Base class describing how a toolchain component is built.

    See Also:
        :class:`BuildRecipe`: Base interface implementing core recipe workflow
    """
    def __init__(self, ctx: BuildContext) -> None:
        super().__init__(ctx, BuildRole.TOOLCHAIN)
    
class SysrootRecipe(BuildRecipe):
    """
    Base class describing how packages installed into the cross
    compilers toolchain should be built.

    See Also:
        :class:`BuildRecipe`: Base interface implementing core recipe workflow
    """
    def __init__(self, ctx: BuildContext) -> None:
        super().__init__(ctx, BuildRole.SYSROOT)
    
class TargetRecipe(BuildRecipe):
    """
    Base class describing how packages targeting the final operating
    system should be built using the cross compiler toolchain.

    See Also:
        :class:`BuildRecipe`: Base interface implementing core recipe workflow
    """
    def __init__(self, ctx: BuildContext) -> None:
        super().__init__(ctx, BuildRole.TARGET)