from pathlib import Path
from builder.recipe import BuildRecipe
from .buildsystem import BuildSystem
from builder.build.context import BuildContext
from dataclasses import dataclass

@dataclass
class CustomBuildSystem(BuildSystem):
    """
    Abstraction for a custom build system.
    """
    def __init__(self, 
                 prepare: str | None = None,
                 configure: str | None = None,
                 build: str | None = None,
                 install: str | None = None,
                 disable_fakeroot: bool = False,
                ):
        self._prepare = prepare
        self._configure = configure
        self._build = build
        self._install = install
        self.disable_fakeroot = disable_fakeroot        

    def _invoke(self, ctx: BuildContext, script: str | None, dir: Path, env: dict[str, str]):
        if not script:
            return

        ctx.run(
            [ "sh", "-c", script ],
            cwd=dir,
            env={ **ctx.env, **env}
        )

    def prepare(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None) -> None:
        """
        Prepare the cross config file for meson.
        """
        self._invoke(recipe.ctx, self._prepare, source_dir, {
            "BUILD": str(build_dir),
            "SOURCE": str(source_dir)
        })

    def configure(self,
                  recipe: BuildRecipe,
                  source_dir: Path, 
                  build_dir: Path,
                  dest_dir: Path|None = None,
                  config_args: list[str]|None = None):
        """
        Configure the project for building.

        This method invokes the ``_configure`` script.

        Args:
            recipe (BuildRecipe): The recipe to build.
            source_dir (Path): Directory containing the projects source tree.
            build_dir (Path): Directory where the build will be configured.
            config_args (list[str] | None, optional): Additional configuration args. Defaults to None.
        """
        self._invoke(recipe.ctx, self._configure, build_dir, {
            "BUILD": str(build_dir),
            "SOURCE": str(source_dir)
        })
        
        
    def build(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Compile the project using the ``_build`` script.

        Args:
            recipe (BuildRecipe): The recipe to build.
            build_dir (Path): Directory containing the configured build tree.
        """
        self._invoke(recipe.ctx, self._build, build_dir, {
            "BUILD": str(build_dir)
        })

    def install(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Install the compiled artifacts using the passed ``_install`` script.

        Args:
            recipe (BuildRecipe): The recipe to build.
            build_dir (Path): Directory containing the build output.
            dest_dir (Path | None, optional): Destination override. Defaults to None.
        """
        dest_dir = dest_dir or build_dir
        dest_dir.mkdir(exist_ok=True, parents=True)
        
        self._invoke(recipe.ctx, self._install, dest_dir, {
            "BUILD": str(build_dir),
            "DESTDIR": str(dest_dir)
        })