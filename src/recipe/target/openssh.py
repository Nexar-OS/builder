from pathlib import Path
from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource
from utils.file import merge_trees

class OpenSSHRecipe(TargetRecipe):
    name = "openssh"
    version = "9.9p2"

    sources = [
        TarballSource(
            name="openssh",
            url=f"https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-{version}.tar.gz",
            md5hash="f617b95fe278bfea8d004589c7a68a85"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr"
        ]
    )

    def prepare(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        """
        Source tree of openssh is packaged in another top-level-directory called "ssh".
        This function strips that top-level-directory.
        """
        return

        merge_trees(
            source_dir / "ssh",
            source_dir
        )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]