import shlex
from pathlib import Path
from builder.recipe import BuildRecipe
from .buildsystem import BuildSystem
from builder.toolchain import Toolchain
from dataclasses import dataclass

@dataclass
class CMake(BuildSystem):
    """Abstraction for the cmake build system."""
    generator: str | None = None

    def prepare(self, recipe: BuildRecipe, toolchain: Toolchain, source_dir: Path, build_dir: Path, dest_dir: Path|None = None) -> None:
        build_dir.mkdir(exist_ok=True, parents=True)

    def configure(self,
                  recipe: BuildRecipe,
                  toolchain: Toolchain,
                  source_dir: Path, 
                  build_dir: Path,
                  dest_dir: Path|None = None,
                  config_args: list[str]|None = None):
        """
        Configure the cmake project for building.

        Args:
            recipe (BuildRecipe): The recipe to build.
            toolchain (Toolchain): The toolchain to use for the build.
            source_dir (Path): Directory containing the projects source tree.
            build_dir (Path): Directory where the build will be configured.
            config_args (list[str] | None, optional): Additional configuration args. Defaults to None.
        """
        args = [
            toolchain.cmake,
            "-S", str(source_dir / self.source_subdir),
            "-B", str(build_dir)
        ]

        if self.generator:
            args.extend([ "-G", self.generator ])
        
        args.extend(self.config_args or [])
        args.extend(config_args or [])

        recipe.shell.run(shlex.join(args), cwd=build_dir)
        
    def build(self, recipe: BuildRecipe, toolchain: Toolchain, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Compile the project using ``cmake``

        Args:
            recipe (BuildRecipe): The recipe to build.
            toolchain (Toolchain): The toolchain to use for the build.
            build_dir (Path): Directory containing the configured build tree.
        """
        recipe.shell.run(
            f"cmake --build {build_dir} --parallel {recipe.ctx.num_jobs} {shlex.join(self.build_args or [])}",
        )

    def install(self, recipe: BuildRecipe, toolchain: Toolchain, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Install the compiled artifacts using ``cmake --install``.

        If ``dest_dir`` is provided, it is passed to ``cmake`` as a
        ``DESTDIR`` override, allowing for staged or relocatable installations.

        Args:
            recipe (BuildRecipe): The recipe to build.
            toolchain (Toolchain): The toolchain to use for the build.
            build_dir (Path): Directory containing the build output.
            dest_dir (Path | None, optional): Destination override. Defaults to None.
        """
        cmd = [ toolchain.cmake ]
        
        if self.install_args:
            cmd.extend(self.install_args)
        
        cmd.append("--install")
        cmd.append(str(build_dir))

        recipe.shell.run(shlex.join(cmd), cwd=build_dir)