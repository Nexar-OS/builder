from build.system import BZip2
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class BZip2Recipe(TargetRecipe):
    name = "bzip2"
    version = "1.0.8" # optional: "latest"

    sources = [
        TarballSource(
            name="bzip2",
            url=f"https://sourceware.org/pub/bzip2/bzip2-{version}.tar.gz",
            md5hash="67e051268d0c475ea773822f7500d0e5"
        )
    ]

    build_method = BuildMethod.IN_SOURCE
    build_system = BZip2()