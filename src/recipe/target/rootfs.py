import shutil
from pathlib import Path
from build import BuildContext
from recipe import TargetRecipe

class RootfsRecipe(TargetRecipe):
    name = "rootfs"
    version = "1.0"

    sources = [ ]

    def post_install(self, ctx: BuildContext, dest_dir: Path | None) -> None:
        """
        Populate the ``dest_dir`` with the basic filesystem layout.
        """
        assert dest_dir, "DESTDIR is required for rootfs recipe."

        for directory in [
            # Root-level directories
            "usr", "etc", "tmp", "var", "root", "dev", "proc", "sys", "run", "mnt", "opt",

            # /usr hierarchy
            "usr/bin", "usr/sbin", "usr/include", "usr/lib", ctx.target_machine.libdir, "usr/share/man", "usr/share/info", "usr/share/doc",

            # /var hierarchy
            "var/cache", "var/lib", "var/log", "var/tmp", "var/run",

            # Runtime directories commonly required by init system
            "run/lock", "run/user"
        ]:
            (dest_dir / directory).mkdir(parents=True, exist_ok=True)
        
        # Set tradition permissions for temp directories
        (dest_dir / "tmp").chmod(0o1777)
        (dest_dir / "var/tmp").chmod(0o1777)

        # usr-merge compatibility symlinks
        for name, target in {
            "bin": "usr/bin",
            "sbin": "usr/sbin",
            "lib": "usr/lib",
            ctx.target_machine.libdir.split("/")[-1]: "usr/lib"
        }.items():
            link = dest_dir / name

            if link.exists() or link.is_symlink():
                link.unlink()
            
            link.symlink_to(target)