from pathlib import Path
from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe, BuildMethod
from builder.source import TarballSource
import shutil

class WPASupplicantRecipe(TargetRecipe):
    name = "wpa_supplicant"
    version = "2.12"

    build_method = BuildMethod.IN_SOURCE

    sources = [
        TarballSource(
            name="wpa_supplicant",
            url=f"https://w1.fi/releases/wpa_supplicant-{version}.tar.gz",
            md5hash="3f1af56655ebca941d2035358331bbc9"
        )
    ]

    build_system = Autotools()

    def prepare(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        shutil.move(
            source_dir / "wpa_supplicant" / "defconfig",
            source_dir / "wpa_supplicant" / ".config"
        )