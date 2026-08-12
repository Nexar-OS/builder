from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class LibcapRecipe(TargetRecipe):
    name = "libcap"
    version = "2.78"
    build_method = BuildMethod.IN_SOURCE
    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libcap",
            url=f"https://www.kernel.org/pub/linux/libs/security/linux-privs/libcap2/libcap-{version}.tar.xz",
            md5hash="0ff11419aa4813c0a0f84fe67bf3b39e"
        )
    ]

    build_system = Autotools(
        build_args=[
            "prefix=/usr",
            "lib=lib"
        ],
        disable_fakeroot=True
    )