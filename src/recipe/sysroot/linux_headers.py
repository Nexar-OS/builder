from pathlib import Path
from build import BuildContext
from build.system import LinuxHeaders
from source import TarballSource
from recipe import (
    SysrootRecipe,
    BuildMethod
)

class LinuxHeadersRecipe(SysrootRecipe):
    name = "linux-headers"
    version = "6.18.42"

    sources = [
        TarballSource(
            name="linux",
            url=f"https://cdn.kernel.org/pub/linux/kernel/v{version.split('.')[0]}.x/linux-{version}.tar.xz",
            md5hash="6f8233a94b0774e64df2bafff25a63d6"
        )
    ]

    build_method = BuildMethod.IN_SOURCE
    
    build_system = LinuxHeaders()