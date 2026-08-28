from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource
from .libpsl import LibpslRecipe
from .libunistring import LibunistringRecipe
from .libidn2 import Libidn2Recipe
from .cacertificate import CaCertificateRecipe

class CurlRecipe(TargetRecipe):
    name = "curl"
    version = "8.21.0"

    depends_on = [
        LibunistringRecipe,
        Libidn2Recipe,
        LibpslRecipe,
        CaCertificateRecipe,
    ]

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="curl",
            url=f"https://github.com/curl/curl/releases/download/curl-{version.replace('.', '_')}/curl-{version}.tar.gz",
            md5hash="6e50e38c398737269ec002749bcc5d0d"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--with-openssl",
            "--disable-shared",
            "--with-ca-bundle=/etc/ssl/certs/ca-certificates.crt",
            "--with-ca-path=/etc/ssl/certs"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]