import shutil
from builder.recipe import BuildRecipe
from pathlib import Path
from .buildsystem import BuildSystem
from builder.build.context import BuildContext

class BZip2(BuildSystem):
    """
    Abstraction for building bzip2.
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
        """
        Builds bzip2 using ``Makefile-libbz2_so``.

        The following commands will be ran:
        - ``make -f Makefile-libbz2_so``
        - ``make clean``
        - ``make``
        """

        recipe.ctx.run(
            [ recipe.ctx.toolchain.make, "-f", "Makefile-libbz2_so" ],
            cwd=build_dir # build dir is source dir
        )

        recipe.ctx.run(
            [ recipe.ctx.toolchain.make, "clean" ],
            cwd=build_dir
        )

        recipe.ctx.run(
            [ recipe.ctx.toolchain.make, f"-j{recipe.ctx.num_jobs}" ],
            cwd=build_dir
        )

    def install(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Install the bzip2 library and binaries into the target destination.

        Args:
            dest_dir (Path | None, optional): Must be passed.
        """
        
        assert dest_dir, "dest_dir argument is required for BZip2"

        usr = dest_dir / "usr"

        (usr / "bin").mkdir(exist_ok=True, parents=True)
        (usr / "share/man/man1").mkdir(exist_ok=True, parents=True)

        # Install shared library
        shutil.copy2(
            build_dir / "bzip2-shared",
            usr / "bin/bzip2"
        )

        # Replace helper binaries with symlinks to bzip2
        for helper in [ "bzcat", "bunzip2" ]:
            link = usr / "bin" / helper

            if link.exists() or link.is_symlink():
                link.unlink()

            link.symlink_to("bzip2")
        
        # Copy man pages
        shutil.copy2(
            build_dir / "bzip2.1",
            usr / "share/man/man1/bzip2.1"
        )