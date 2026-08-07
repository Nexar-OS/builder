from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe
from source import TarballSource

class FileRecipe(TargetRecipe):
    name = "file"
    version = "5.48"

    sources = [
        TarballSource(
            name="file",
            url=f"https://astron.com/pub/file/file-{version}.tar.gz",
            md5hash="423686e97f731d8c24e9cd1a22b03dec"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr"
        ],
        disable_fakeroot=True # ``file -C -m magic`` core dumps when using fakeroot
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]