from build import BuildContext
from build.system import Meson
from recipe import TargetRecipe
from source import TarballSource

class GlibRecipe(TargetRecipe):
    name = "glib"
    maj_version = "2.89"
    version = f"{maj_version}.3"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="glib",
            url=f"https://download.gnome.org/sources/glib/{maj_version}/glib-{version}.tar.xz",
            md5hash="a00f19c6efdf9ecf1b51d0597d7931cd"
        )
    ]

    build_system = Meson(
        config_args=[
            "--prefix=/usr",

            "-Ddtrace=disabled",
            "-Dintrospection=disabled"
        ]
    )