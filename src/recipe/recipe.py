from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass

from source.source import Source
from build.context import BuildContext
from utils.logger import info

@dataclass
class BuildRecipe(ABC):
    name: str
    version: str
        
    sources: list[Source]

    def _resolve_sources(self, source_dir: Path):
        """Prepare the sources for the build process.
        
        This step includes downloading and installing them into their respective destinations.

        Args:
            source_dir (Path): The source directory for sources to be put into.
        """
        
        for source in self.sources:
            source.install(source_dir)

    def work_dir(self, ctx: BuildContext) -> Path:
        """Creates work directory for this recipe instance.

        Args:
            ctx (BuildContext): Context used for the build.

        Returns:
            Path: Path where the build takes place
        """
        work_dir = ctx.build_dir / self.name
        work_dir.mkdir(exist_ok=True, parents=True)

        return work_dir.resolve()

    @abstractmethod
    def _install_path(self, ctx: BuildContext) -> Path:
        """Creates the path for the build to be generated into.

        Args:
            ctx (BuildContext): Context used for the build.

        Returns:
            Path: The path for the final build to be installed into.
        """
        raise NotImplementedError()

    def build(self, ctx: BuildContext) -> None:
        """Build the recipe using the current BuildContext as configuration basis.

        Args:
            ctx (BuildContext): Context used for the build.
        """

        work_dir = self.work_dir(ctx)
        build_dir = work_dir / "build"
        source_dir = work_dir / "sources"
        dest_dir = self._install_path(ctx)

        build_dir.mkdir(exist_ok=True, parents=True)
        source_dir.mkdir(exist_ok=True, parents=True)

        info(f"Building recipe '{self.name}-{self.version}' using \n{work_dir=}\n{build_dir=}\n{source_dir=}\n{dest_dir=}")

        self._resolve_sources(source_dir)

        # Let recipes prepare their environment
        self.prepare(ctx, source_dir, build_dir)

        # Let recipes apply custom patches
        self.patch(ctx, source_dir)

        # Run installation
        # TODO
        ...

        # Run post install hook
        self.post_install(ctx, source_dir, build_dir)

    def patch(self, ctx: BuildContext, source_dir: Path) -> None:
        """
        Allow recipes to apply custom source-patches.

        Args:
            ctx (BuildContext): Context used for current build.
            source_dir (Path): The directory to where the source was installed into.
        """
        ...

    def prepare(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        """
        Let recipes prepare their environment before installation starts.

        Args:
            ctx (BuildContext): Context used for current build.
            source_dir (Path): The directory to where the source was installed into.
            build_dir (Path): Directory where the recipe will be build in.
        """
        ...

    def post_install(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        """Post install hook.
        """
        ...