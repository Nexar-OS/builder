from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class OpenSSLRecipe(TargetRecipe):
    name = "openssl"
    version = "3.6.3"

    copy_to_toolchain = True
    _export_to_toolchain = [
        "etc/ssl",
        "usr"
    ]

    sources = [
        TarballSource(
            name="openssl",
            url=f"https://github.com/openssl/openssl/releases/download/openssl-{version}/openssl-{version}.tar.gz",
            md5hash="f388d6144fe20b9b2c6bf208280d6ec3"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--openssldir=/etc/ssl",
            "shared"
        ],
        disable_fakeroot=True
    )