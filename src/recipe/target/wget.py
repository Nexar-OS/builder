from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class WgetRecipe(TargetRecipe):
    name = "wget"
    version = "1.25.0"

    sources = [
        TarballSource(
            name="wget",
            url=f"https://ftp.gnu.org/gnu/wget/wget-{version}.tar.gz",
            md5hash="c70ba58b36f944e8ba1d655ace552881"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--with-openssl",
            "--with-ssl=openssl"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]