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
            "usr", "etc", "tmp", "var", "root", "home", "dev", "proc", "sys", "run", "mnt", "opt",

            # /usr hierarchy
            "usr/bin", "usr/include", "usr/lib", ctx.target_machine.libdir, "usr/share/man", "usr/share/info", "usr/share/doc",

            # /var hierarchy
            "var/cache", "var/lib", "var/log", "var/tmp", "var/run", "var/mail",

            # Runtime directories commonly required by init system
            "run/lock", "run/user"
        ]:
            (dest_dir / directory).mkdir(parents=True, exist_ok=True)
        
        # Set tradition permissions for temp directories
        (dest_dir / "tmp").chmod(0o1777)
        (dest_dir / "var/mail").chmod(0o755)
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

        # Create /etc/passwd
        (dest_dir / "etc/passwd").write_text(
            "root:x:0:0::/root:/usr/bin/bash\n"
        )
        ctx.run([ "chown", "0:0", str(dest_dir / "etc/passwd") ])
        (dest_dir / "etc/passwd").chmod(0o644)

        # Create /etc/group
        (dest_dir / "etc/group").write_text(
            "root:x:0:\n"
            "mail:x:12:\n"
        )
        ctx.run([ "chown", "0:0", str(dest_dir / "etc/group") ])
        (dest_dir / "etc/group").chmod(0o644)
        
        # Create /etc/shadow
        (dest_dir / "etc/shadow").write_text(
            "root:$6$Qqy4FrIwYO/AYIuJ$ZrN10dVJ8p34.JIrsPVfZnO39h9ZRA8WTwAZEcNPKEUUR2Ju8O3zk0lvuXzydbRmduO7YWzi788zLWbxEBsCV/:2000:0:99999:7:::\n"
        )
        ctx.run([ "chown", "0:0", str(dest_dir / "etc/shadow") ])
        (dest_dir / "etc/shadow").chmod(0o644)

        # Create /etc/nsswitch.conf
        (dest_dir / "etc/nsswitch.conf").write_text(
            "passwd: files\n"
            "group: files\n"
            "shadow: files\n"
        )
        ctx.run([ "chown", "0:0", str(dest_dir / "etc/nsswitch.conf") ])
        (dest_dir / "etc/nsswitch.conf").chmod(0o644)

        # Create /etc/pam.d/login
        pamd = dest_dir / "etc/pam.d"
        pamd.mkdir(parents=True, exist_ok=True)

        (pamd / "passwd").write_text(
            "#%PAM-1.0\n"
            "auth            required         pam_unix.so\n"
            "account         required         pam_unix.so\n"
            "password        required         pam_unix.so\n"
        )

        (pamd / "login").write_text(
            "#%PAM-1.0\n"
            "\n"
            "auth       requisite    pam_nologin.so\n"
            "auth       required      pam_unix.so\n"
            "account    required      pam_unix.so\n"
            "session    required      pam_unix.so\n"
            "password   required      pam_unix.so\n"
        )

        # Create os-release
        (dest_dir / "etc/os-release").write_text(
            'NAME="NexarOS"\n'
            'PRETTY_NAME="NexarOS"\n'
            'ID=nexar\n'
            'BUILD_ID=rolling\n'
            'ANSI_COLOR="38;2;23;147;209"\n'
            'HOME_URL=""\n'
            'DOCUMENTATION_URL=""\n'
            'SUPPORT_URL=""\n'
            'BUG_REPORT_URL=""\n'
            'PRIVACY_POLICY_URL=""\n'
            'LOGO=archlinux-logo\n'
        )