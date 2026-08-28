from pathlib import Path
from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class BashRecipe(TargetRecipe):
    name = "bash"
    version = "5.3"

    sources = [
        TarballSource(
            name="bash",
            url=f"https://ftp.gnu.org/gnu/bash/bash-{version}.tar.gz",
            md5hash="977c8c0c5ae6309191e7768e28ebc951"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--with-bash-malloc"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]
    
    def post_install(self, ctx: BuildContext, dest_dir: Path | None) -> None:
        """
        Creates a symlink from sh to bash.
        """
        if not dest_dir:
            return

        bin = dest_dir / "bin"
        bin.mkdir(exist_ok=True, parents=True)


        (bin / "sh").symlink_to("bash")