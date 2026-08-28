from pathlib import Path
from .buildsystem import BuildSystem
from builder.build.context import BuildContext
from builder.utils.logger import error, info
from dataclasses import dataclass

@dataclass
class CMake(BuildSystem):
    """Abstraction for the cmake build system."""
    generator: str | None = None

    def prepare(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        build_dir.mkdir(exist_ok=True, parents=True)

    def configure(self,
                  ctx: BuildContext,
                  source_dir: Path,
                  build_dir: Path,
                  config_args: list[str] | None = None):
        """
        Configure the cmake project for building.

        Args:
            ctx (BuildContext): Build context.
            source_dir (Path): Directory containing the projects source tree.
            build_dir (Path): Directory where the build will be configured.
            config_args (list[str] | None, optional): Additional configuration args. Defaults to None.
        """
        args = [
            ctx.toolchain.cmake,
            "-S", str(source_dir),
            "-B", str(build_dir)
        ]

        if self.generator:
            args.extend([ "-G", self.generator ])
        
        args.extend(self.config_args or [])
        args.extend(config_args or [])

        ctx.run(args, cwd=build_dir)
        
    def build(self, ctx: BuildContext, build_dir: Path):
        """
        Compile the project using ``cmake``

        Args:
            ctx (BuildContext): Build context.
            build_dir (Path): Directory containing the configured build tree.
        """
        ctx.run(
            [
                "cmake",
                "--build",
                str(build_dir),
                "--parallel",
                str(ctx.num_jobs),
                *(self.build_args or [])
            ]
        )

    def install(self, ctx: BuildContext, build_dir: Path, dest_dir: Path | None = None):
        """
        Install the compiled artifacts using ``cmake --install``.

        If ``dest_dir`` is provided, it is passed to ``cmake`` as a
        ``DESTDIR`` override, allowing for staged or relocatable installations.

        Args:
            ctx (BuildContext): Build context.
            build_dir (Path): Directory containing the build output.
            dest_dir (Path | None, optional): Destination override. Defaults to None.
        """
        cmd = [ ctx.toolchain.make ]

        if dest_dir:
            cmd.append(f"DESTDIR={dest_dir}")
        
        if self.install_args:
            cmd.extend(self.install_args)
        
        cmd.append("install")


        ctx.run(cmd, cwd=build_dir)