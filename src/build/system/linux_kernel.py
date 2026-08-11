import shutil
from pathlib import Path
from .buildsystem import BuildSystem
from build.context import BuildContext

class LinuxKernel(BuildSystem):
    """
    Abstraction for building the linux kernel modules and headers.
    """

    def prepare(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        # Not needed
        pass

    def configure(self,
                  ctx: BuildContext,
                  source_dir: Path,
                  build_dir: Path,
                  config_args: list[str] | None = None):
        """
        Configure the linux kernel using ``make defconfig``

        Args:
            config_args (list[str] | None, optional): Optional additional arguments to the ``make defconfig`` command. Defaults to None.
        """

        # Build argument list
        args = list(self.config_args or [])
        args += config_args or []

        ctx.run(
            [
                ctx.toolchain.make,
                f"ARCH={ctx.target_machine.kernel_arch}",
                f"CROSS_COMPILE={ctx.target_machine.triple}-",
                "defconfig",
                *args
            ],
            cwd=build_dir
        )


    def build(self, ctx: BuildContext, build_dir: Path):
        """
        Build the linux kernel modules and kernel image.
        This function invokes the ``make`` command.

        Args:
            ctx (BuildContext): _description_
            build_dir (Path): _description_
        """

        ctx.run(
            [
                ctx.toolchain.make,
                f"ARCH={ctx.target_machine.kernel_arch}",
                f"CROSS_COMPILE={ctx.target_machine.triple}-",
                *(self.build_args or []),
                f"-j{ctx.num_jobs}"
            ],
            cwd=build_dir,
            use_fakeroot=False
        )

    def install(self, ctx: BuildContext, build_dir: Path, dest_dir: Path | None = None):
        """
        Install the linux kernel modules and install them into a set destination directory.

        This function
        - installs the kernel modules using ``make modules_install``.
        - copies the architecture respective kernel image.

        Args:
            ctx (BuildContext): Build context.
            dest_dir (Path | None, optional): Destination override. Defaults to None.
        """
        
        assert dest_dir, "dest_dir argument is required for LinuxKernel"

        # Install kernel modules
        ctx.run(
            [
                ctx.toolchain.make,
                f"ARCH={ctx.target_machine.kernel_arch}",
                f"CROSS_COMPILE={ctx.target_machine.triple}-",
                "modules_install",
                f"INSTALL_MOD_PATH={dest_dir}",
                *(self.install_args or [])
            ],
            cwd=build_dir
        )

        # Copy kernel image
        image = {
            "x86": ("arch/x86/boot/bzImage", "vmlinuz"),
            "arm64": ("arch/arm64/boot/Image", "Image"),
            "arm": ("arch/arm/boot/Image", "zImage"),
            "riscv": ("arch/riscv/boot/Image", "Image"),
        }.get(ctx.target_machine.kernel_arch)

        if not image:
            raise RuntimeError("Unsupported target kernel architecture!")

        dest = dest_dir / "boot"
        dest.mkdir(exist_ok=True, parents=True)

        shutil.copy2(
            str(build_dir / image[0]),
            str(dest_dir / "boot" / image[1])
        )