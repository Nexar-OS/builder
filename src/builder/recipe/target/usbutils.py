from builder.build.system import Meson
from builder.recipe import TargetRecipe
from builder.source import TarballSource
from builder.recipe.target.libusb import LibusbRecipe

# TODO:
# USBUtils depends on libudev which is part of systemd
class USButilsRecipe(TargetRecipe):
    name = "usb-utils"
    version = "018"

    depends_on = [
        LibusbRecipe()
    ]

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