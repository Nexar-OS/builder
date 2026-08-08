from build.system import Pciutils
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class PciutilsRecipe(TargetRecipe):
    name = "pciutils"
    version = "2.8"

    sources = [
        TarballSource(
            name="pciutils",
            url=f"https://www.kernel.org/pub/software/utils/pciutils/pciutils-3.15.0.tar.xz",
            md5hash="03d151c0ba42527701ba28aca34093e7"
        )
    ]

    build_method = BuildMethod.IN_SOURCE
    build_system = Pciutils()