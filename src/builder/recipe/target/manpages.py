from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource

class ManPagesRecipe(TargetRecipe):
    name = "manpages"
    version = "5.13"

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="manpages",
            url=f"https://github.com/mkerrisk/man-pages/archive/refs/tags/man-pages-{version}.tar.gz",
            md5hash="d0fc0d9268ad93995cad414140c34da0"
        )
    ]

    build_system = Autotools(skip_build=True)