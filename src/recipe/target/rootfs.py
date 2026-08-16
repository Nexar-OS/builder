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
            "usr/bin", "usr/include", "usr/lib", ctx.target_machine.libdir, "usr/share/man", "usr/share/info", "usr/share/doc",

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
            "sbin": "usr/bin",
            "usr/sbin": "bin",
            "lib": "usr/lib",
            ctx.target_machine.libdir.split("/")[-1]: "usr/lib"
        }.items():
            link = dest_dir / name

            if link.exists() or link.is_symlink():
                link.unlink()
            
            link.symlink_to(target)
        

        # Create minimal /etc/passwd
        with (dest_dir / "etc/passwd").open("w") as f:
            f.write("root:x:0:0::/root:/usr/bin/bash\n")
        
        # Create minimal /etc/group
        with (dest_dir / "etc/group").open("w") as f:
            f.write("root:x:0:")
        
        # Create minimal /etc/shadow
        with (dest_dir / "etc/shadow").open("w") as f:
            # hash is for password "test"
            f.write("root:$6$Qqy4FrIwYO/AYIuJ$ZrN10dVJ8p34.JIrsPVfZnO39h9ZRA8WTwAZEcNPKEUUR2Ju8O3zk0lvuXzydbRmduO7YWzi788zLWbxEBsCV/:2000:0:99999:7:::")

        # Create minimal /etc/nsswitch
        with (dest_dir / "etc/nsswitch").open("w") as f:
            f.write("passwd: files\n")
            f.write("group: files\n")
            f.write("shadow: files\n")
        
        # Create minimal /etc/pam.d/login
        (dest_dir / "etc/pam.d/").mkdir(exist_ok=True, parents=True)
        with (dest_dir / "etc/pam.d/login").open("w") as f:
            # f.write("#%PAM-1.0\n\n")

            f.write("auth       required      pam_unix.so\n")
            f.write("account    required      pam_unix.so\n")
            f.write("session    required      pam_unix.so\n")