from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource
from .libmnl import LibmnlRecipe
from .libnftnl import LibnftnlRecipe
from .gmp import GMPRecipe
from .libedit import LibeditRecipe

class NFtablesRecipe(TargetRecipe):
    name = "nftables"
    version = "1.1.6"

    depends_on = [
        LibmnlRecipe(),
        LibnftnlRecipe(),
        GMPRecipe(),
        LibeditRecipe()
    ]

    sources = [
        TarballSource(
            name="nftables",
            url=f"https://www.netfilter.org/pub/nftables/nftables-{version}.tar.xz",
            md5hash="638ddff35ca429f68860a437d53237b4"
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