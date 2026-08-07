from pathlib import Path
import subprocess
from build import BuildContext
from recipe import TargetRecipe
import shutil

class LibstdcxxRuntimeRecipe(TargetRecipe):
    name = "libstdc++-runtime"
    version = "2.44"

    # Libstdc++ is built directly with gcc
    sources = [ ]

    def post_install(self, ctx: BuildContext, dest_dir: Path | None) -> None:
        """
        Export a copy of libstdc++ from toolchain.
        """
        assert dest_dir, "Libstdc++ cannot be installed without a DESTDIR."

        # Find path to lib in sysroot
        gxx = ctx.cross_toolchain_dir / "bin" / f"{ctx.target_machine.triple}-g++"
        lib = Path(subprocess.check_output(
            [ str(gxx), "--print-file-name=libstdc++.so.6" ],
            text=True
        ).strip())

        if not lib.exists():
            raise FileNotFoundError(f"libstdc++ not found: {str(lib)}")

        # Copy to libdir
        dest = dest_dir / ctx.target_machine.libdir
        dest.mkdir(exist_ok=True, parents=True)

        shutil.copy2(
            str(lib),
            str(dest)
        )