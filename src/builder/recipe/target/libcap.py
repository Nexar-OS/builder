from pathlib import Path
from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource
from builder.utils.file import merge_trees

class LibcapRecipe(TargetRecipe):
    name = "libcap"
    version = "2.78"
    build_method = BuildMethod.IN_SOURCE

    _export_to_toolchain = [
        "usr/lib",
        "usr/lib64",
        "usr/include",
    ]

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libcap",
            url=f"https://www.kernel.org/pub/linux/libs/security/linux-privs/libcap2/libcap-{version}.tar.xz",
            md5hash="0ff11419aa4813c0a0f84fe67bf3b39e"
        )
    ]

    build_system = Autotools(
        build_args=[
            "prefix=/usr",
            "lib=lib"
        ],
        disable_fakeroot=True
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--host={ctx.target_machine.triple}",
            f"--build={ctx.build_machine.triple}"
        ]
    
    def post_install(self, ctx: BuildContext, dest_dir: Path | None) -> None:
        """
        Moves the library from /lib(64) to /usr/lib(64)
        """
        if not dest_dir:
            return

        libdir = ctx.target_machine.libdir
        libdir_name = libdir.split("/")[-1]

        merge_trees(
            dest_dir / libdir_name,
            dest_dir / libdir
        )