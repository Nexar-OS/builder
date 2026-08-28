from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource
from .efivar import EfivarRecipe
from .libpopt import LibpoptRecipe

class EfibootmgrRecipe(TargetRecipe):
    name = "efibootmgr"
    version = "9.11"

    depends_on = [
        EfivarRecipe,
        LibpoptRecipe,
    ]

    copy_to_toolchain = True

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="efibootmgr",
            url=f"https://github.com/rhboot/efibootmgr/releases/download/18/efibootmgr-18.tar.bz2",
            md5hash="a92ce8fd2b282fa30f066797b14095ef"
        )
    ]

    efidir = "BOOT"

    build_system = Autotools(
        build_args=[f"EFIDIR={efidir}"],
        install_args=[f"EFIDIR={efidir}"]
    )