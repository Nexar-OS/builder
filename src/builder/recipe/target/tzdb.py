from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource

class TzdbRecipe(TargetRecipe):
    name = "tzdb"
    version = "2026c"

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="tzdb",
            url=f"https://data.iana.org/time-zones/releases/tzdb-{version}.tar.lz",
            md5hash="b20a51bf4c062509d35f377a99a52507"
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