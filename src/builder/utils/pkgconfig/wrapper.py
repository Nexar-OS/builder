import shutil
from pathlib import Path

def load_pkgconfig_wrapper(dest: Path):
    """Copy the pkgconfig_wrapper file into a desired destination.

    PKG_CONFIG_SYSROOT_DIR is required for normal --cflags/--libs queries,
    but pkg-config also applies it to --variable results.
        
    For --variable queries, only run the real pkg-config without
    the PKG_CONFIG_SYSROOT_DIR environment variable provided by the toolchain env.

    All other queries retain normal sysroot behavior.

    Args:
        dest (Path): Final path (with filename).
    """

    wrapper = Path(__file__).parent / "pkgconfig_wrapper"

    shutil.copy2(wrapper, dest)

    dest.chmod(0o755)