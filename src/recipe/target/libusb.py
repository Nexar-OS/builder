from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class LibusbRecipe(TargetRecipe):
    name = "libusb"
    version = "1.0.30"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libusb",
            url=f"https://github.com/libusb/libusb/releases/download/v{version}/libusb-{version}.tar.bz2",
            md5hash="b0b0bacc2c6919515db8e863f0517db8"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]