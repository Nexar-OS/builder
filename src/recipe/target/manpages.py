from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

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