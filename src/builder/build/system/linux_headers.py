from pathlib import Path
from builder.recipe import BuildRecipe
from .buildsystem import BuildSystem
from builder.build.context import BuildContext

class LinuxHeaders(BuildSystem):
    """
    Abstraction for building the linux headers.
    """

    def prepare(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None) -> None:
        # Not needed
        pass

    def configure(self,
                  recipe: BuildRecipe,
                  source_dir: Path, 
                  build_dir: Path,
                  dest_dir: Path|None = None,
                  config_args: list[str]|None = None):
        # Not needed
        pass

    def build(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        # Not needed
        pass

    def install(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Install the linux headers using ``make headers_install``.

        Args:
            recipe (BuildRecipe): The recipe to build.
            dest_dir (Path | None, optional): Destination override. Defaults to None.
        """
        
        assert dest_dir, "dest_dir argument is required for LinuxHeaders"

        recipe.ctx.run(
            [
                recipe.ctx.toolchain.make,
                f"ARCH={recipe.ctx.target_machine.kernel_arch}",
                "headers_install",
                f"INSTALL_HDR_PATH={dest_dir / 'usr'}"
            ],
            cwd=build_dir
        )