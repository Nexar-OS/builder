from build.context import BuildContext
from build.system import LinuxKernel
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class KernelRecipe(TargetRecipe):
    name = "kernel"
    version = "6.18.42"

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="linux",
            url=f"https://cdn.kernel.org/pub/linux/kernel/v{version.split('.')[0]}.x/linux-{version}.tar.xz",
            md5hash="6f8233a94b0774e64df2bafff25a63d6"
        )
    ]

    build_system = LinuxKernel(version=version)