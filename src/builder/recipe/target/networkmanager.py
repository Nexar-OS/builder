from builder.build.system import Meson
from builder.recipe import TargetRecipe
from builder.source import TarballSource
from .libndp import LibndpRecipe
from .nss import NssRecipe
from .libpsl import LibpslRecipe

class NetworkManagerRecipe(TargetRecipe):
    name = "NetworkManager"
    version = "1.58.0"

    depends_on = [
        LibndpRecipe,
        NssRecipe,
        LibpslRecipe
    ]

    sources = [
        TarballSource(
            name="NetworkManager",
            url=f"https://github.com/NetworkManager/NetworkManager/archive/refs/tags/{version}.tar.gz",
            md5hash="09703e646e13321c6991bf77bb904042"
        )
    ]

    build_system = Meson(
        config_args=[
            "--prefix=/usr",
            "-Dintrospection=false",
            "-Dselinux=false",
            "-Dclat=false",
            "-Dlibaudit=no",
            "-Dpolkit=false",
            "-Dcrypto=nss",
            "-Dppp=false",
            "-Dmodem_manager=false",
            "-Dovs=false",

            # Newt appears to be deprecated
            "-Dnmtui=false",

            "-Dnm_cloud_setup=false",
            "-Dnbft=false",
            "-Dman=false"
        ]
    )