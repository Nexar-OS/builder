from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from ..context import BuildContext

@dataclass
class BuildSystem(ABC):
    """
    Abstract interface for build system implementations.

    A ``BuildSystem`` defines the operations required to prepare, configure,
    compile, and install a project within the recipe-driven build pipeline.
    """
    config_args: list[str]|None = None
    build_args: list[str]|None = None
    install_args: list[str]|None = None

    @abstractmethod
    def prepare(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        """Hook for preparing the build system.

        Args:
            ctx (BuildContext): Current build context.
            source_dir (Path): Directory with source trees.
            build_dir (Path): Directory to build in.
        """
        raise NotImplementedError()

    @abstractmethod
    def configure(self, ctx: BuildContext, source_dir: Path, build_dir: Path, config_args: list[str]|None = None):
        """Configure the build system.

        Args:
            ctx (BuildContext): Current build context.
            source_dir (Path): Directory with source trees.
            build_dir (Path): Directory to build in.
            config_args (list[str] | None, optional): Additional configuration args
        """
        raise NotImplementedError()

    @abstractmethod
    def build(self, ctx: BuildContext, build_dir: Path):
        """Start the build

        Args:
            ctx (BuildContext): Current build context.
            build_dir (Path): Directory to build in.
        """
        raise NotImplementedError()
    
    @abstractmethod
    def install(self, ctx: BuildContext, build_dir: Path, dest_dir: Path|None = None):
        """Install the build into the final destination.

        Args:
            ctx (BuildContext): Current build context.
            build_dir (Path): Directory where the source was build in.
            dest_dir (Path | None, optional): Final destination. Defaults to None.
        """
        pass
