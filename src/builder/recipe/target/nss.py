from pathlib import Path
from builder.build import BuildContext
from builder.build.system import NSS
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource
from builder.utils.file import merge_trees

class NssRecipe(TargetRecipe):
    name = "nss"
    version = "3.127-with-nspr-4.39"

    copy_to_toolchain = True
    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="nss",
            url=f"https://ftp.mozilla.org/pub/security/nss/releases/NSS_{version.split('-')[0].replace('.', '_')}_RTM/src/nss-{version}.tar.gz",
            md5hash="bbdd7a0b7b4433e3d1dc4bbba1603b5f"
        )
    ]

    build_system = NSS()