from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource
from .libaio import LibaioRecipe

class Lvm2Recipe(TargetRecipe):
    name = "lvm2"
    version = "2.03.42"

    depends_on = [
        LibaioRecipe(),
    ]


    build_method = BuildMethod.IN_SOURCE
    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="lvm2",
            url=f"https://sourceware.org/ftp/lvm2/LVM2.{version}.tgz",
            md5hash="1cfc17fcbdc5103492b4504c5ddaa274"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]