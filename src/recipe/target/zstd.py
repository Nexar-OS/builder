from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class ZStdRecipe(TargetRecipe):
    name = "zstd"
    version = "1.5.7"

    sources = [
        TarballSource(
            name="zstd",
            url=f"https://github.com/facebook/zstd/releases/download/v{version}/zstd-{version}.tar.gz",
            md5hash="780fc1896922b1bc52a4e90980cdda48"
        )
    ]

    build_method = BuildMethod.IN_SOURCE
    build_system = Autotools(
        build_args=[
            "PREFIX=/usr"
        ],
        install_args=[
            "PREFIX=/usr"
        ]
    )