from builder.build.system import Meson
from builder.recipe import TargetRecipe
from builder.source import TarballSource
from builder.recipe.target import *
from builder.recipe.toolchain import GperfRecipe

class SystemdRecipe(TargetRecipe):
    name = "systemd"
    version = "259.8"

    copy_to_toolchain = True

    depends_on = [
        DbusRecipe(),
        GperfRecipe(),
        BZip2Recipe()
    ]

    sources = [
        TarballSource(
            name="systemd",
            url=f"https://github.com/systemd/systemd/archive/refs/tags/v{version}.tar.gz",
            md5hash="af9f9fb1aae5bfab603d7820b35ac6c9"
        )
    ]

    build_system = Meson(
        config_args=[
            "--prefix=/usr",
            "--sysconfdir=/etc",
            "--localstatedir=/var",
            "-Dstatic-libsystemd=false",
            "-Dfirstboot=false",
            "-Dtests=false",
            "-Dsysusers=True",
            "-Dtmpfiles=true"
        ],
        disable_fakeroot=True
    )