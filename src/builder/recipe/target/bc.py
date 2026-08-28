from pathlib import Path
from builder.build import BuildContext
from builder.build.system import Autotools
from builder.recipe import TargetRecipe
from builder.source import TarballSource
import re

class BcRecipe(TargetRecipe):
    name = "bc"
    version = "7.0.3"

    sources = [
        TarballSource(
            name="bc",
            url=f"https://github.com/gavinhoward/bc/releases/download/{version}/bc-{version}.tar.gz",
            md5hash="a020c36c383624119cce4d2cf5d13388"
        )
    ]

    build_system = Autotools(
        config_args=[
            "--prefix=/usr",
            "--disable-dc"
        ]
    )

    def patch(self, ctx: BuildContext, source_dir: Path) -> None:
        """
        Patch for compatability with GCC 16.

        bc uses UINTMAX_C() with boolean values in BC_PARSE_EXPR_ENTRY.
        GCC 16 expands these as falseUL/trueUL, which are invalid C identifiers.
        """

        bc_header = source_dir / "include" / "bc.h"

        content = bc_header.read_text()
        content = re.sub(
            r"UINTMAX_C\((e[1-8])\)", r"((uintmax_t) (\1))",
            content
        )
        bc_header.write_text(content)