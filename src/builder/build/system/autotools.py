from pathlib import Path
from .buildsystem import BuildSystem
from builder.recipe import BuildRecipe, BuildRole
from builder.build.context import BuildContext
from builder.utils.logger import error, info
from dataclasses import dataclass

@dataclass
class Autotools(BuildSystem):
    """Abstraction for the autotools build system.

    Args:
        BuildSystem (_type_): _description_
    """
    skip_build: bool = False
    install_target: str = "install"
    disable_fakeroot: bool = False

    def prepare(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None) -> None:
        # Not needed
        pass

    def configure(self,
                  recipe: BuildRecipe,
                  source_dir: Path, 
                  build_dir: Path,
                  dest_dir: Path|None = None,
                  config_args: list[str]|None = None):
        """
        Configure the Autotools project for building.

        The method locates the supported configuration script in ``source_dir``
        and executes it with the passed arguments.

        Args:
            recipe (BuildRecipe): The recipe to build.
            source_dir (Path): Directory containing the projects source tree.
            build_dir (Path): Directory where the build will be configured.
            config_args (list[str] | None, optional): Additional configuration args. Defaults to None.
        """

        build_dir.mkdir(exist_ok=True, parents=True)

        # Build argument list
        args = list(self.config_args or [])
        # args += config_args or []

        match recipe.build_role:
            case BuildRole.TARGET | BuildRole.SYSROOT:
                args += [
                    f"--host={recipe.ctx.target_machine.triple}",
                    f"--build={recipe.ctx.build_machine.triple}"
                ]
            
            case BuildRole.TOOLCHAIN:
                args += [
                    f"--build={recipe.ctx.build_machine.triple}",
                    f"--host={recipe.ctx.build_machine.triple}",
                    f"--target={recipe.ctx.target_machine.triple}",
                    f"--prefix={recipe.ctx.toolchain_dir}",
                    f"--with-sysroot={recipe.ctx.toolchain_sysroot}"
                ]

        # No config args were passed means no configuration will be invoked
        if not args:
            info("No config args passed. Skipping configuration.")
            return

        # Find config script
        # Different projects might use different names for the same config file
        config_script = None
        for name in [ "configure", "Configure", "config" ]:
            config_script = source_dir / name

            if config_script.is_file():
                break

        # Edge case: if the last checked entry doesn't exist
        if config_script and not config_script.is_file():
            error(f"Autotools failed to find config script in '{source_dir}'")
            return

        # Execute config script
        recipe.ctx.run(
            [
                str(config_script),
                *args
            ],
            cwd=build_dir,
            use_fakeroot=not self.disable_fakeroot
        )
        
    def build(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Compile the project using ``make``

        Args:
            ctx (BuildContext): Build context.
            build_dir (Path): Directory containing the configured build tree.
        """
        if self.skip_build:
            return
        
        recipe.ctx.run(
            [recipe.ctx.toolchain.make, *(self.build_args or []), f"-j{recipe.ctx.num_jobs}"],
            cwd=build_dir,
            use_fakeroot=not self.disable_fakeroot
        )

    def install(self, recipe: BuildRecipe, source_dir: Path, build_dir: Path, dest_dir: Path|None = None):
        """
        Install the compiled artifacts using ``make install``.

        If ``dest_dir`` is provided, it is passed to ``make`` as a
        ``DESTDIR`` override, allowing for staged or relocatable installations.

        Args:
            ctx (BuildContext): Build context.
            build_dir (Path): Directory containing the build output.
            dest_dir (Path | None, optional): Destination override. Defaults to None.
        """
        cmd = [ recipe.ctx.toolchain.make ]

        if dest_dir:
            cmd.append(f"DESTDIR={dest_dir}")
        
        if self.install_args:
            cmd.extend(self.install_args)
        
        cmd.append(self.install_target)

        recipe.ctx.run(cmd, cwd=build_dir, use_fakeroot=not self.disable_fakeroot)

        # Strip .la files
        recipe.ctx.run([
            "find", str(dest_dir), "-type", "f", "-name", "*.la", "-delete"
        ])