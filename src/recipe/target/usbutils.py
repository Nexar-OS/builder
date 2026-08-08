from build import BuildContext
from build.system import Meson
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

# TODO:
# USBUtils depends on libudev which is part of systemd
class USButilsRecipe(TargetRecipe):
    name = "usb-utils"
    version = "018"

    sources = [
        TarballSource(
            name="usb-utils",
            url=f"https://www.kernel.org/pub/linux/utils/usb/usbutils/usbutils-{version}.tar.xz",
            md5hash="0a351e2241c50a1f026a455dccf24d73"
        )
    ]

    build_system = Meson([
        "--sysconfdir=/etc",
        "--localstatedir=/var"
    ])