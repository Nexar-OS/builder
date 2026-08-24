from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class AclRecipe(TargetRecipe):
    name = "acl"
    version = "3.6.8"

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="acl",
            url=f"https://github.com/acl-dev/acl/archive/refs/tags/v{version}.tar.gz",
            md5hash="881f42227acf59dadc9c2b12b9422352"
        )
    ]

    build_system = Autotools()