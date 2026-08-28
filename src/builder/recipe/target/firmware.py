from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource

class FirmwareRecipe(TargetRecipe):
    name = "firmware"
    version = "20260810"

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="firmware",
            url=f"https://gitlab.com/kernel-firmware/linux-firmware/-/archive/{version}/linux-firmware-{version}.tar.gz",
            md5hash="00c461b744f06359d1280c0fa73418ae"
        )
    ]

    build_system = Autotools()