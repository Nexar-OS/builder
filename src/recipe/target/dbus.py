from build import BuildContext
from build.system import Meson
from recipe import TargetRecipe
from source import TarballSource

class DbusRecipe(TargetRecipe):
    name = "dbus"
    version = "1.16.2"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="dbus",
            url=f"https://dbus.freedesktop.org/releases/dbus/dbus-{version}.tar.xz",
            md5hash="97832e6f0a260936d28536e5349c22e5"
        )
    ]

    build_system = Meson(
        config_args=[
            "--prefix=/usr",
            "--sysconfdir=/etc",
            "--localstatedir=/var"
        ],
        disable_fakeroot=True
    )