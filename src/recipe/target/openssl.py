from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class OpenSSLRecipe(TargetRecipe):
    name = "openssl"
    version = "4.0.1"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="openssl",
            url=f"https://github.com/openssl/openssl/releases/download/openssl-{version}/openssl-{version}.tar.gz",
            md5hash="07e316afe26b61e72206b81706b497bb"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr"
        ],
        disable_fakeroot=True
    )