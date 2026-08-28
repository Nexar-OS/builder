from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from ..context import BuildContext
from builder.recipe import BuildRecipe

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
    def prepare(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None) -> None:
        """Hook for preparing the build system.

        Args:
            recipe (BuildRecipe): The recipe to build.
            source_dir (Path): Directory with source trees.
            build_dir (Path): Directory to build in.
        """
        raise NotImplementedError()

    @abstractmethod
    def configure(self,
                  recipe: BuildRecipe,
                  source_dir: Path, 
                  build_dir: Path,
                  dest_dir: Path|None = None,
                  config_args: list[str]|None = None):
        """Configure the build system.

        Args:
            recipe (BuildRecipe): The recipe to build.
            source_dir (Path): Directory with source trees.
            build_dir (Path): Directory to build in.
            config_args (list[str] | None, optional): Additional configuration args
        """
        raise NotImplementedError()

    @abstractmethod
    def build(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """Start the build

        Args:
            recipe (BuildRecipe): The recipe to build.
            build_dir (Path): Directory to build in.
        """
        raise NotImplementedError()
    
    @abstractmethod
    def install(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """Install the build into the final destination.

        Args:
            recipe (BuildRecipe): The recipe to build.
            build_dir (Path): Directory where the source was build in.
            dest_dir (Path | None, optional): Final destination. Defaults to None.
        """
        pass
