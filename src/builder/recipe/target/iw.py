from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource
from .libnl import LibnlRecipe

class IwRecipe(TargetRecipe):
    name = "iw"
    version = "6.17"

    depends_on = [
        LibnlRecipe,
    ]

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="iw",
            url=f"https://www.kernel.org/pub/software/network/iw/iw-{version}.tar.xz",
            md5hash="7323e43843f30068ffb6079e15e8e11a"
        )
    ]

    build_system = Autotools(
    )