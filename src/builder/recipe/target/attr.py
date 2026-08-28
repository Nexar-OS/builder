from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource

class AttrRecipe(TargetRecipe):
    name = "attr"
    version = "2.6.0"

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="attr",
            url=f"http://download.savannah.gnu.org/releases/attr/attr-{version}.tar.xz",
            md5hash="c0516a99377b4938eeb7fb2699247e82"
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