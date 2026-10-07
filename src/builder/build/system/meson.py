from pathlib import Path
from builder.recipe import BuildRecipe
from .buildsystem import BuildSystem
from builder.toolchain import Toolchain, NativeToolchain
from dataclasses import dataclass

@dataclass
class Meson(BuildSystem):
    """
    Abstraction for the meson build system.
    """
    disable_fakeroot: bool = False
    install_target: str | None = None

    def prepare(self, recipe: BuildRecipe, toolchain: Toolchain, source_dir: Path, build_dir: Path, dest_dir: Path|None = None) -> None:
        """
        Prepare the cross config file for meson.
        """

        if isinstance(toolchain, NativeToolchain):
            return

        self.cross_file = build_dir / "cross.ini"
        with self.cross_file.open("w") as f:
            f.write("[binaries]\n")
            f.write(f"c = '{toolchain.cc}'\n")
            f.write(f"cpp = '{toolchain.cxx}'\n")
            f.write(f"ar = '{toolchain.ar}'\n")
            f.write(f"strip = '{toolchain.strip}'\n")
            f.write(f"pkg-config = '{toolchain.pkg_config}'\n")

            f.write("[host_machine]\n")
            f.write("system = 'linux'\n")
            f.write(f"cpu_family = '{toolchain.target.arch}'\n")
            f.write(f"cpu = '{toolchain.target.arch}'\n")
            f.write("endian = 'little'\n")

            f.write("[properties]\n")
            f.write(f"sys_root = '{toolchain.sysroot}'\n")
            f.write(f"pkg_config_libdir = '{toolchain.pkg_config_libdir}'\n")

            f.write("[built-in options]\n")
            f.write(f"default_library = 'shared'\n")
            f.write(f"prefer_static = true\n")
        
        native = NativeToolchain()
        self.native_file = build_dir / "native.ini"
        with self.native_file.open("w") as f:
            f.write("[binaries]\n")
            f.write(f"pkg-config = '{native.pkg_config}'\n")

            f.write("[properties]\n")
            f.write(f"sys_root = '{recipe.ctx.toolchain_host_tools}'\n")
            f.write(f"pkg_config_libdir = '{recipe.ctx.toolchain_host_tools / 'usr/lib/pkgconfig'}'\n")

    def configure(self,
                  recipe: BuildRecipe,
                  toolchain: Toolchain,
                  source_dir: Path, 
                  build_dir: Path,
                  dest_dir: Path|None = None,
                  config_args: list[str]|None = None):
        """
        Configure the meson project for building.

        This method invokes the ``meson setup`` command.

        Args:
            recipe (BuildRecipe): The recipe to build.
            toolchain (Toolchain): The toolchain to use for the build.
            source_dir (Path): Directory containing the projects source tree.
            build_dir (Path): Directory where the build will be configured.
            config_args (list[str] | None, optional): Additional configuration args. Defaults to None.
        """

        build_dir.mkdir(exist_ok=True, parents=True)

        # Build argument list
        args = list(self.config_args or [])
        args += config_args or []

        # No config args were passed means no configuration will be invoked
        if not args:
            recipe.logger.info("No config args passed. Skipping configuration.")
            return

        cmd = [
            str(toolchain.meson),
            "setup", str(build_dir), str(source_dir),
            *args,
            "--prefer-static",
        ]

        if not isinstance(toolchain, NativeToolchain):
            assert self.cross_file, "No cross file found!"
            assert self.native_file, "No native file found!"
            cmd += [
                "--cross-file",
                str(self.cross_file),
                "--native-file",
                str(self.native_file),
            ]
        
            

        # Invoke setup
        recipe.ctx.run(
            cmd,
            cwd=build_dir,
            use_fakeroot=not self.disable_fakeroot,
            recipe=recipe
        )
        
    def build(self, recipe: BuildRecipe, toolchain: Toolchain, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Compile the project using ``ninja``

        Args:
            recipe (BuildRecipe): The recipe to build.
            toolchain (Toolchain): The toolchain to use for the build.
            build_dir (Path): Directory containing the configured build tree.
        """
        cmd = [toolchain.ninja, *(self.build_args or []), "-C", str(build_dir)]

        if self.install_target:
            cmd += [ self.install_target ]

        recipe.ctx.run(
            cmd,
            cwd=build_dir,
            use_fakeroot=not self.disable_fakeroot,
            recipe=recipe
        )

    def install(self, recipe: BuildRecipe, toolchain: Toolchain, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Install the compiled artifacts using ``ninja install``.

        If ``dest_dir`` is provided, it is passed to ``ninja`` as a
        ``DESTDIR`` override, allowing for staged or relocatable installations.

        Args:
            recipe (BuildRecipe): The recipe to build.
            toolchain (Toolchain): The toolchain to use for the build.
            build_dir (Path): Directory containing the build output.
            dest_dir (Path | None, optional): Destination override. Defaults to None.
        """
        cmd = [ toolchain.ninja ]

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
            env=env,
            recipe=recipe
        )