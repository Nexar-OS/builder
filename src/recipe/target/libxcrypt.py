from build import BuildContext
from build.system import Autotools
from recipe import TargetRecipe, BuildMethod
from source import TarballSource

class LibxcryptRecipe(TargetRecipe):
    name = "libxcrypt"
    version = "4.5.2"
    copy_to_toolchain = True

    sources = [
        TarballSource(
            name="libxcrypt",
            url=f"https://github.com/besser82/libxcrypt/releases/download/v{version}/libxcrypt-{version}.tar.xz",
            md5hash="25e888919ddcd153a07daa95224fa436"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--disable-werror",
            "--prefix=/usr",
            "--disable-static"
        ]
    )

    def _config_args(self, ctx: BuildContext) -> list[str]:
        return [
            f"--host={ctx.target_machine.triple}",
            f"--build={ctx.build_machine.triple}"
        ]