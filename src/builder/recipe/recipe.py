from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum, auto

import time
import json
from hashlib import sha256

from builder.source.source import Source
from builder.build.context import BuildContext
from builder.build.system import BuildSystem
from builder.utils.logger import info, warn
from builder.utils.file import rmtree, merge_trees

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

class BuildMethod(Enum):
    """
    Describes where the source and build tree should be located.
    """

    IN_SOURCE = auto()
    """
    Build will run inside of the source-tree.
    """

    OUT_OF_SOURCE  = auto()
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
    def __init__(self, role: BuildRole) -> None:
        super().__init__()

        self.build_role = role

    dependencies: list["BuildRecipe"] = []
    opt_dependencies: list["BuildRecipe"] = []
    build_dependencies: list["BuildRecipe"] = []

    name: str
    version: str

    sources: list[Source]

    build_method: BuildMethod = BuildMethod.OUT_OF_SOURCE  # most recipes are build out-of-source
    
    build_system: BuildSystem|None = None

    def fingerprint(self, ctx: BuildContext) -> str:
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

        # Build system args
        config_args = self._config_args(ctx)
        build_args = None
        install_args = None
        if self.build_system:
            if self.build_system.config_args:
                config_args = config_args + self.build_system.config_args

            build_args = self.build_system.build_args
            install_args = self.build_system.install_args

        h.update(f"{config_args}-{build_args}-{install_args}".encode())

        return h.hexdigest()

    def metadata_path(self, ctx: BuildContext) -> Path:
        """
        Return the path to the recipe's build metadata file.

        Returns:
            Path: Path to the JSON metadata file for this recipe.
        """
        path = ctx.metadata_dir / "recipes" / f"{self.name}.json"
        path.parent.mkdir(exist_ok=True, parents=True)

        return path

    def needs_rebuild(self, ctx: BuildContext) -> bool:
        """
        Determine whether the recipe must be rebuilt.

        A rebuild is required if no metadata from a previous build exists or 
        if the stored fingerprint differs from the fingerprint computed from
        the current recipe state.

        Returns:
            bool: True if the recipe should be rebuilt, otherwise False.
        """
        path = self.metadata_path(ctx)

        if not path.exists():
            return True
        
        old = json.loads(path.read_text())["fingerprint"]
        return old != self.fingerprint(ctx)

    def mark_built(self, ctx: BuildContext) -> None:
        """
        Record the current recipe fingerprint as successfully built.
        """
        path = self.metadata_path(ctx)
        path.write_text(
            json.dumps(
                asdict(RecipeMetadata(
                    name=self.name,
                    fingerprint=self.fingerprint(ctx),
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

    def work_dir(self, ctx: BuildContext) -> Path:
        """
        Create and return the working directory for this recipe.

        The working directory is derived from ``ctx.build_dir`` and the recipe name and version.

        Args:
            ctx (BuildContext): Context used for the build.

        Returns:
            Path: Absolute path where the build takes place
        """
        work_dir = ctx.build_dir / "recipe" / (self.name + "-" + self.version)
        work_dir.mkdir(exist_ok=True, parents=True)

        return work_dir.resolve()

    def _install_path(self, ctx: BuildContext) -> Path|None:
        """
        Return the directory where the build should be installed.

        Path is determined by the build role, this recipe was constructed with:

        ``BuildRole.TOOLCHAIN``: $ctx.cross_toolchain_dir
        ``BuildRole.SYSROOT``: $ctx.cross_toolchain_sysroot
        ``BuildRole.TARGET``: $work_dir/rootfs

        Args:
            ctx (BuildContext): Context used for the build.

        Returns:
            Path: The path for the final build to be installed into.
        """
        match self.build_role:
            case BuildRole.TOOLCHAIN:
                return ctx.cross_toolchain_dir

            case BuildRole.SYSROOT:
                return ctx.cross_toolchain_sysroot
            
            case BuildRole.TARGET:
                return self.work_dir(ctx) / "rootfs"

        raise NotImplementedError(
            f"Build role not supported: '{self.build_role}'"
        )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        """
        Generate build-system configuration arguments for this recipe.

        Args:
            ctx (BuildContext): Build context.

        Returns:
            list[str]: List of configuration args passed to the build system.
        """
        return []

    def _install(self, ctx: BuildContext, build_dir: Path, dest_dir: Path|None):
        """
        Invoke the install call to the build system.

        Args:
            ctx (BuildContext): Context used for current build.
            build_dir (Path): Directory where the build system already build the binaries into.
            dest_dir (Path): Destination directory to install the files into.
        """
        assert self.build_system, "No build system complete installation!"

        self.build_system.install(ctx, build_dir, dest_dir)

    def build(self, ctx: BuildContext) -> None:
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
            ctx (BuildContext): Context used for the build.
        """

        work_dir = self.work_dir(ctx)
        build_dir = work_dir / "build"
        source_dir = work_dir / "sources"
        dest_dir = self._install_path(ctx)

        # Ensure a fresh empty build directory
        if build_dir.is_dir():
            rmtree(build_dir)

        build_dir.mkdir(exist_ok=True, parents=True)
        source_dir.mkdir(exist_ok=True, parents=True)

        info(f"Building recipe '{self.name}-{self.version}' using \n{work_dir=}\n{build_dir=}\n{source_dir=}\n{dest_dir=}")

        self._resolve_sources(source_dir, build_dir)

        # Fix source directory passed to build system
        if self.build_method == BuildMethod.IN_SOURCE:
            source_dir = build_dir

        # Let recipes prepare their environment
        self.prepare(ctx, source_dir, build_dir)

        # Let recipes apply custom patches
        self.patch(ctx, source_dir)

        # Run installation
        if self.build_system:
            self.build_system.prepare(ctx, source_dir, build_dir)
            self.build_system.configure(ctx, source_dir, build_dir, self._config_args(ctx))
            self.build_system.build(ctx, build_dir)
        
            self._install(ctx, build_dir, dest_dir)

        # Run post install hook
        self.post_install(ctx, dest_dir)

        self.mark_built(ctx)

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
                 role: BuildRole,
                 name: str,
                 version: str,
                 sources: list[Source],
                 dependencies: list[BuildRecipe]|None = None,
                 opt_dependencies: list[BuildRecipe]|None = None,
                 build_dependencies: list[BuildRecipe]|None = None,
                 build_method: BuildMethod = BuildMethod.OUT_OF_SOURCE,
                 build_system: BuildSystem|None = None
                 ) -> None:
        super().__init__(role)

        self.name = name
        self.version = version
        self.sources = sources
        self.dependencies = dependencies or []
        self.opt_dependencies = opt_dependencies or []
        self.build_dependencies = build_dependencies or []
        self.build_method = build_method
        self.build_system = build_system

class ToolchainRecipe(BuildRecipe):
    """
    Base class describing how a toolchain component is built.

    See Also:
        :class:`BuildRecipe`: Base interface implementing core recipe workflow
    """
    def __init__(self) -> None:
        super().__init__(BuildRole.TOOLCHAIN)
    
class SysrootRecipe(BuildRecipe):
    """
    Base class describing how packages installed into the cross
    compilers toolchain should be built.

    See Also:
        :class:`BuildRecipe`: Base interface implementing core recipe workflow
    """
    def __init__(self) -> None:
        super().__init__(BuildRole.SYSROOT)
    
class TargetRecipe(BuildRecipe):
    """
    Base class describing how packages targeting the final operating
    system should be built using the cross compiler toolchain.

    See Also:
        :class:`BuildRecipe`: Base interface implementing core recipe workflow
    """
    def __init__(self) -> None:
        super().__init__(BuildRole.TARGET)

    depends_on: list[BuildRecipe]|None = None

    copy_to_toolchain: bool = False

    _export_to_toolchain: list[str] = [
        "usr/lib",
        "usr/lib64",
        "usr/include",
        "usr/lib/pkgconfig",
        "usr/share/pkgconfig"
    ]

    def _export_to_sysroot(self, ctx: BuildContext) -> None:
        """
        Export the build package into sysroot for future packages
        to be able to link against it.
        """
        root = self._install_path(ctx)

        if not root:
            return

        for relative in self._export_to_toolchain:
            source = root / relative
            dest = ctx.cross_toolchain_sysroot / relative

            if not source.exists():
                continue

            info(f"Merging '{relative}' from '{self.name}' into sysroot.")
            merge_trees(
                source,
                dest,
                copy=True,
                skip_extensions=[
                    "la"
                ]
            )

    def _clean_rootfs(self, ctx: BuildContext):
        """
        Cleans the root filesystem where the package will be installed into.
        This prevents configuration contamination over multiple runs within
        the same build directory.
        """

        dest = self._install_path(ctx)
        if not dest:
            warn(f"Dest of TargetRecipe '{self.name}' is None.")
            return

        # Delete old run
        rmtree(dest)

    def _resolve_dependencies(self, ctx: BuildContext):
        """
        Tries to invoke the build of all required dependency recipes.

        If the recipe is already marked as built in metadata-cache,
        it will be skipped.
        """
        if not self.depends_on:
            return
        
        for dependency in self.depends_on:
            info(f"Resolving dependency '{dependency.name}' for '{self.name}'")
            if not dependency.needs_rebuild(ctx):
                info(f"Dependency '{dependency.name}' was already built!")
                continue

            dependency.build(ctx)


    def build(self, ctx: BuildContext):
        """
        Invokes default recipe build behavior after cleaning the
        installation destination.
        """

        self._clean_rootfs(ctx)
        self._resolve_dependencies(ctx)

        super().build(ctx)

        if self.copy_to_toolchain:
            self._export_to_sysroot(ctx)