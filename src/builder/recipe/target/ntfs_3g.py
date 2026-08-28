from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource

class Ntfs3gRecipe(TargetRecipe):
    name = "ntfs-3g"
    version = "2026.7.7"

    sources = [
        TarballSource(
            name="ntfs-3g",
            url=f"https://tuxera.com/opensource/ntfs-3g_ntfsprogs-{version}.tgz",
            md5hash="d8a84db2a56bed3cec8547801c5b56e9"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--with-fuse=internal",
            "--disable-ldconfig"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]