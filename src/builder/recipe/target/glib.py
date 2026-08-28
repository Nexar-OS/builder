from builder.build import BuildContext
from builder.build.system import Meson
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class GlibRecipe(TargetRecipe):
    name = "glib"
    maj_version = "2.89"
    version = f"{maj_version}.3"

    copy_to_toolchain = True

    _export_to_toolchain = [
        "usr/bin",
        "usr/include",
        "usr/lib",
        "usr/share"
    ]

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