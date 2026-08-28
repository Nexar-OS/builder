from builder.build import BuildContext
from builder.build.system import Meson
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class IpUtilsRecipe(TargetRecipe):
    name = "iputils"
    version = "20250605"

    sources = [
        TarballSource(
            name="iputils",
            url=f"https://github.com/iputils/iputils/releases/download/{version}/iputils-{version}.tar.gz",
            md5hash="3597adefcfe416222cb71e57b513cd03"
        )
    ]

    build_system = Meson(
        config_args=[
            "--prefix=/usr"
        ]
    )