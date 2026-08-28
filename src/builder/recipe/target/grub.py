from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource
from .efibootmgr import EfibootmgrRecipe

class GrubRecipe(TargetRecipe):
    name = "grub"
    version = "2.14"

    depends_on = [
        EfibootmgrRecipe(),
    ]

    sources = [
        TarballSource(
            name="grub",
            url=f"https://ftp.gnu.org/gnu/grub/grub-{version}.tar.xz",
            md5hash="383f9effad01c235d2535357ff717543"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--bindir=/usr/bin",
            "--sbindir=/usr/bin",
            "--mandir=/usr/share/man",
            "--infodir=/usr/share/info",
            "--datarootdir=/usr/share",
            "--sysconfdir=/etc",
            "--with-bootdir=/boot",
            "--with-grubdir=grub",
            "--with-platform=efi"
        ],
        build_args=[
            "CFLAGS=-Wno-error"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--build={ctx.build_machine.triple}",
            f"--host={ctx.target_machine.triple}"
        ]