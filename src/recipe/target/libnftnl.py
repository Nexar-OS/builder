from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class LibnftnlRecipe(TargetRecipe):
    name = "libnftnl"
    version = "1.3.1"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libnftnl",
            url=f"https://www.netfilter.org/pub/libnftnl/libnftnl-{version}.tar.xz",
            md5hash="ab1a894717469fb1d45d4c8ca0557fb6"
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