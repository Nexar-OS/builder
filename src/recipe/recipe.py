from pathlib import Path
from abc import ABC, abstractmethod
from enum import Enum, auto

from source.source import Source
from build.context import BuildContext
from build.system import BuildSystem
from utils.logger import info, warn
from utils.file import rmtree, merge_trees

class BuildMethod(Enum):
    """
    Build will run inside of the source-tree.
    """
    IN_SOURCE = auto()

    """
    Build will run in a separate directory than the source-tree.
    """
    OUT_OF_SOURCE  = auto()

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
    name: str
    version: str

    sources: list[Source]

    build_method: BuildMethod = BuildMethod.OUT_OF_SOURCE  # most recipes are build out-of-source
    
    build_system: BuildSystem|None = None

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
        work_dir = ctx.build_dir / (self.name + "-" + self.version)
        work_dir.mkdir(exist_ok=True, parents=True)

        return work_dir.resolve()

    @abstractmethod
    def _install_path(self, ctx: BuildContext) -> Path|None:
        """
        Return the directory where the build should be installed.

        Subclasses must implement this method.

        Args:
            ctx (BuildContext): Context used for the build.

        Returns:
            Path: The path for the final build to be installed into.
        """    
        raise NotImplementedError()

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

class ToolchainRecipe(BuildRecipe):
    """
    Base class describing how a toolchain component is built.

    See Also:
        :class:`BuildRecipe`: Base interface implementing core recipe workflow
    """

    def _install_path(self, ctx: BuildContext) -> Path|None:
        # Binutils/GCC expect to be installed into --prefix directly
        return None
    
class SysrootRecipe(BuildRecipe):
    """
    Base class describing how packages installed into the cross
    compilers toolchain should be built.

    See Also:
        :class:`BuildRecipe`: Base interface implementing core recipe workflow
    """

    def _install_path(self, ctx: BuildContext) -> Path | None:
        return ctx.cross_toolchain_sysroot
    
class TargetRecipe(BuildRecipe):
    """
    Base class describing how packages targeting the final operating
    system should be built using the cross compiler toolchain.

    See Also:
        :class:`BuildRecipe`: Base interface implementing core recipe workflow
    """

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
                copy=True
            )

    def _install_path(self, ctx: BuildContext) -> Path | None:
        return self.work_dir(ctx) / "rootfs"

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
    
    def export(self, ctx: BuildContext, dest: Path):
        """
        Exports the final rootfs the package was installed into
        to its final destination.
        """

        rootfs = self._install_path(ctx)
        if not rootfs:
            return
        
        merge_trees(
            rootfs,
            dest,
            copy=False
        )

    def build(self, ctx: BuildContext):
        """
        Invokes default recipe build behavior after cleaning the
        installation destination.
        """

        self._clean_rootfs(ctx)

        super().build(ctx)

        if self.copy_to_toolchain:
            self._export_to_sysroot(ctx)