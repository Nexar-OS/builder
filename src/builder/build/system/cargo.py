import shlex
from pathlib import Path
from .buildsystem import BuildSystem
from builder.recipe import BuildRecipe
from builder.toolchain import Toolchain
from dataclasses import dataclass

@dataclass
class Cargo(BuildSystem):
    """
    Abstraction for the cargo build system.
    """
    disable_fakeroot: bool = False

    # Cargo build options
    install_subdir: str | None = None
    release: bool = True
    locked: bool = True
    offline: bool = True

    def _run(self, recipe: BuildRecipe, args: list[str], cwd: Path):
        command = [
            "env",
            "CARGO_HTTP_MULTIPLEXING=false",
            "CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse",
            *args
        ]

        recipe.shell.run(
            shlex.join(command),
            cwd=cwd
        )

    def _manifest(self, source_dir: Path) -> Path:
        manifest = source_dir / "Cargo.toml"
        if not manifest.is_file():
            raise FileNotFoundError(f"No Cargo.toml found in {source_dir}")

        return manifest

    def _cargo_args(self, source_dir: Path, build_dir: Path) -> list[str]:
        args = [
            "--manifest-path", str(self._manifest(source_dir)),
            "--target-dir", str(build_dir)
        ]

        if self.locked:
            args.append("--locked")
        
        if self.offline:
            args.append("--offline")

        return args

    def prepare(self, recipe: BuildRecipe, toolchain: Toolchain, source_dir: Path, build_dir: Path, dest_dir: Path|None = None) -> None:
        self._manifest(source_dir)
        build_dir.mkdir(exist_ok=True, parents=True)

    def configure(self,
                  recipe: BuildRecipe,
                  toolchain: Toolchain,
                  source_dir: Path, 
                  build_dir: Path,
                  dest_dir: Path|None = None,
                  config_args: list[str]|None = None):
        """
        Configure the Cargo project for building.

        Args:
            recipe (BuildRecipe): The recipe to build.
            toolchain (Toolchain): The toolchain to use for the build.
            source_dir (Path): Directory containing the projects source tree.
            build_dir (Path): Directory where the build will be configured.
            config_args (list[str] | None, optional): Additional configuration args. Defaults to None.
        """

        args = [
            "cargo",
            "metadata",
            "--no-deps",
            "--format-version", "1",
            "--manifest-path",
            str(self._manifest(source_dir))
        ]

        config_args = (self.config_args or []) + (config_args or [])
        if config_args:
            args.extend(config_args)

        # Execute config script
        self._run(
            recipe=recipe,
            args=args,
            cwd=build_dir
        )
        
    def build(self, recipe: BuildRecipe, toolchain: Toolchain, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Compile the project using ``cargo``

        Args:
            recipe (BuildRecipe): The recipe to build.
            toolchain (Toolchain): The toolchain to use for the build.
            build_dir (Path): Directory containing the configured build tree.
        """
        args = [
            "cargo", "build",
            *self._cargo_args(source_dir, build_dir),
            f"--jobs={recipe.ctx.num_jobs}"
        ]

        if self.build_args:
            args.extend(self.build_args)

        self._run(
            recipe=recipe,
            args=args,
            cwd=build_dir
        )

    def install(self, recipe: BuildRecipe, toolchain: Toolchain, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Install the compiled artifacts.

        If ``dest_dir`` is provided, it is passed to ``cargo``,
        allowing for staged or relocatable installations.

        Args:
            recipe (BuildRecipe): The recipe to build.
            toolchain (Toolchain): The toolchain to use for the build.
            build_dir (Path): Directory containing the build output.
            dest_dir (Path | None, optional): Destination override. Defaults to None.
        """
        if not dest_dir:
            raise ValueError("Cargo installation requires dest_dir!")

        # Optionally branch to subdir
        if self.install_subdir:
            source_dir /= self.install_subdir

        args = [
            "cargo", "install",
            "--path", str(source_dir),
            "--root", str(dest_dir),
            "--target-dir", str(build_dir),
            "--jobs", str(recipe.ctx.num_jobs)
        ]

        if self.locked:
            args.append("--locked")
        
        if self.offline:
            args.append("--offline")
        
        if self.release:
            args.append("--profile")
            args.append("release")
        
        if self.install_args:
            args.extend(self.install_args)

        self._run(
            recipe=recipe,
            args=args,
            cwd=build_dir
        )

        (dest_dir / ".crates.toml").unlink(True)
        (dest_dir / ".crates2.json").unlink(True)