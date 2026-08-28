from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource

class EfivarRecipe(TargetRecipe):
    name = "efivar"
    version = "39"

    build_method = BuildMethod.IN_SOURCE

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="efivar",
            url=f"https://github.com/rhboot/efivar/archive/refs/tags/{version}.tar.gz",
            md5hash="a8fc3e79336cd6e738ab44f9bc96a5aa"
        )
    ]

    build_system = Autotools(
        install_args=[
            "LIBDIR=/usr/lib64"
        ]
    )