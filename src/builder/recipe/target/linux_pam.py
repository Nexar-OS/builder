from builder.build import BuildContext
from builder.build.system import Meson
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource

class LinuxPamRecipe(TargetRecipe):
    name = "linux-pam"
    version = "1.7.2"
    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="linux-pam",
            url=f"https://github.com/linux-pam/linux-pam/releases/download/v{version}/Linux-PAM-{version}.tar.xz",
            md5hash="934c26eca3fada956356a30489e86291"
        )
    ]

    build_system = Meson(
        config_args=[
            "--prefix=/usr",
            "--sysconfdir=/etc"
        ],
        disable_fakeroot=True
    )