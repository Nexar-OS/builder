from build import BuildContext
from build.system import CMake
from recipe import TargetRecipe
from source import TarballSource

class JsonCRecipe(TargetRecipe):
    name = "json-c"
    version = "0.19-20260627"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="json-c",
            url=f"https://github.com/json-c/json-c/releases/download/json-c-{version}/json-c-{version.split('-')[0]}.tar.gz",
            md5hash="5678f1373ba51e0041b574c0411c696b"
        )
    ]

    build_system = CMake(
        config_args=[
            "-DCMAKE_INSTALL_PREFIX=/usr"
        ]
    )