from pathlib import Path
from build import BuildContext
from recipe import TargetRecipe
from source import FileSource
import shutil

class CaCertificateRecipe(TargetRecipe):
    name = "ca-certificate"
    version = "2026-08-13"

    sources = [
        FileSource(
            name="curl-ca-cert",
            url=f"https://curl.se/ca/cacert-{version}.pem",
            md5hash="b7a0a25670b6987c14b542d83212af4e",
            filename="ca-certificates.crt"
        )
    ]

    def prepare(self, ctx: BuildContext, source_dir: Path, build_dir: Path) -> None:
        """
        Caches the source dir for the post_install hook to be able
        to access the sources directory.
        """
        self.source_dir = source_dir

    def post_install(self, ctx: BuildContext, dest_dir: Path | None) -> None:
        """
        Installs the curl ca-cert.pem into the dest dirs root filesystem.
        """
        if not dest_dir:
            return

        cert_dir = dest_dir / "etc" / "ssl" / "certs"
        cert_dir.mkdir(parents=True, exist_ok=True)

        shutil.copy2(
            self.source_dir / "ca-certificates.crt",
            cert_dir
        )

        cert_link = dest_dir / "etc" / "ssl" / "cert.pem"
        if cert_link.exists() or cert_link.is_symlink():
            cert_link.unlink()
        
        cert_link.symlink_to("/etc/ssl/certs/ca-certificates.crt")