from pathlib import Path
import subprocess
from builder.build import BuildContext
from builder.recipe import TargetRecipe
import shutil

class LibgccRuntimeRecipe(TargetRecipe):
    name = "libgcc-runtime"
    version = "2.44"

    # Libgcc is built directly with gcc
    sources = [ ]

    def post_install(self, ctx: BuildContext, dest_dir: Path | None) -> None:
        """
        Export a copy of libgcc from toolchain.
        """
        assert dest_dir, "Libgcc cannot be installed without a DESTDIR."

        # Find path to lib in sysroot
        gcc = ctx.cross_toolchain_dir / "bin" / f"{ctx.target_machine.triple}-gcc"
        lib = Path(subprocess.check_output(
            [ str(gcc), "--print-file-name=libgcc_s.so.1" ],
            text=True
        ).strip())

        if not lib.exists():
            raise FileNotFoundError(f"libgcc not found: {str(lib)}")

        # Copy to libdir
        dest = dest_dir / ctx.target_machine.libdir
        dest.mkdir(exist_ok=True, parents=True)

        shutil.copy2(
            str(lib),
            str(dest)
        )