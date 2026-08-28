from pathlib import Path
from builder.recipe import BuildRecipe
from .buildsystem import BuildSystem
from builder.build.context import BuildContext
from builder.utils.logger import error, info
from dataclasses import dataclass

@dataclass
class Meson(BuildSystem):
    """
    Abstraction for the meson build system.
    """
    disable_fakeroot: bool = False

    def prepare(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None) -> None:
        """
        Prepare the cross config file for meson.
        """

        self.cross_file = build_dir / "cross.ini"
        with self.cross_file.open("w") as f:
            f.write("[binaries]\n")
            f.write(f"c = '{recipe.ctx.toolchain.cc}'\n")
            f.write(f"cpp = '{recipe.ctx.toolchain.cxx}'\n")
            f.write(f"ar = '{recipe.ctx.toolchain.ar}'\n")
            f.write(f"strip = '{recipe.ctx.toolchain.strip}'\n")
            f.write(f"pkgconfig = '{recipe.ctx.toolchain.pkg_config}'\n")

            f.write("[host_machine]\n")
            f.write("system = 'linux'\n")
            f.write(f"cpu_family = '{recipe.ctx.target_machine.arch}'\n")
            f.write(f"cpu = '{recipe.ctx.target_machine.arch}'\n")
            f.write("endian = 'little'\n")

            f.write("[properties]\n")
            f.write(f"sys_root = '{recipe.ctx.toolchain.sysroot}'\n")
            f.write(f"pkg_config_libdir = '{recipe.ctx.toolchain.env.get('PKG_CONFIG_LIBDIR', '')}'\n")

            f.write("[built-in options]\n")
            f.write(f"default_library = 'shared'\n")
            f.write(f"prefer_static = true\n")

    def configure(self,
                  recipe: BuildRecipe,
                  source_dir: Path, 
                  build_dir: Path,
                  dest_dir: Path|None = None,
                  config_args: list[str]|None = None):
        """
        Configure the meson project for building.

        This method invokes the ``meson setup`` command.

        Args:
            recipe (BuildRecipe): The recipe to build.
            source_dir (Path): Directory containing the projects source tree.
            build_dir (Path): Directory where the build will be configured.
            config_args (list[str] | None, optional): Additional configuration args. Defaults to None.
        """
        assert self.cross_file, "No cross file found!"

        build_dir.mkdir(exist_ok=True, parents=True)

        # Build argument list
        args = list(self.config_args or [])
        args += config_args or []

        # No config args were passed means no configuration will be invoked
        if not args:
            info("No config args passed. Skipping configuration.")
            return

        # Invoke setup
        recipe.ctx.run(
            [
                str(recipe.ctx.toolchain.meson),
                "setup", str(build_dir), str(source_dir),
                *args,
                "--cross-file",
                str(self.cross_file),
                "--prefer-static"
            ],
            cwd=build_dir,
            use_fakeroot=not self.disable_fakeroot
        )
        
    def build(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Compile the project using ``ninja``

        Args:
            recipe (BuildRecipe): The recipe to build.
            build_dir (Path): Directory containing the configured build tree.
        """
        recipe.ctx.run(
            [recipe.ctx.toolchain.ninja, *(self.build_args or []), "-C", str(build_dir)],
            cwd=build_dir,
            use_fakeroot=not self.disable_fakeroot
        )

    def install(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Install the compiled artifacts using ``ninja install``.

        If ``dest_dir`` is provided, it is passed to ``ninja`` as a
        ``DESTDIR`` override, allowing for staged or relocatable installations.

        Args:
            recipe (BuildRecipe): The recipe to build.
            build_dir (Path): Directory containing the build output.
            dest_dir (Path | None, optional): Destination override. Defaults to None.
        """
        cmd = [ recipe.ctx.toolchain.ninja ]

        # Destdir must be passed as an environment variable
        env = dict(recipe.ctx.env)
        if dest_dir:
            dest_dir.mkdir(parents=True, exist_ok=True)
            env["DESTDIR"] = str(dest_dir)
        
        if self.install_args:
            cmd.extend(self.install_args)
        
        cmd += [ "-C", str(build_dir), "install" ]

        recipe.ctx.run(
            cmd,
            cwd=build_dir,
            use_fakeroot=not self.disable_fakeroot,
            env=env
        )