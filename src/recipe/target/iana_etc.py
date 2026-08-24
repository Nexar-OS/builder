from pathlib import Path
from build import BuildContext
from recipe import TargetRecipe
from source import TarballSource
from utils.file import merge_trees

class IanaEtcRecipe(TargetRecipe):
    name = "ianaetc"
    version = "20260817"

    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="ianaetc",
            url=f"https://github.com/Mic92/iana-etc/releases/download/{version}/iana-etc-{version}.tar.gz",
            md5hash="351dce747398f9595c7b643820cec017"
        )
    ]

    def prepare(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        self.source_dir = source_dir
    
    def post_install(self, ctx: BuildContext, dest_dir: Path | None) -> None:
        """
        Copies the protocols and sources files from the source into
        the final destination rootfs.
        """
        if not dest_dir:
            return
        
        merge_trees(
            self.source_dir / "protocols",
            dest_dir / "etc"
        )

        merge_trees(
            self.source_dir / "services",
            dest_dir / "etc"
        )