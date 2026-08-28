from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource

class LibaioRecipe(TargetRecipe):
    name = "libaio"
    version = "0.3.113"

    build_method = BuildMethod.IN_SOURCE

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libaio",
            url=f"https://releases.pagure.org/libaio/libaio-{version}.tar.gz",
            md5hash="7d5be185f20eeaae15e267419950aaf7"
        )
    ]

    build_system = Autotools()