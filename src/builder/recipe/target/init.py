import stat
from pathlib import Path
from builder.build import BuildContext
from builder.recipe import TargetRecipe

class InitRecipe(TargetRecipe):
    """
    A basic init script for testing.
    """
    name = "init"
    version = "1.0"

    sources = [ ]

    def post_install(self, ctx: BuildContext, dest_dir: Path | None) -> None:
        if not dest_dir:
            return
        
        sbin = dest_dir / "sbin"
        sbin.mkdir(exist_ok=True, parents=True)

        init = sbin / "init"

        with init.open("w") as f:
            f.write("#!/bin/bash\n")
            f.write("mount -t proc proc /proc\n")
            f.write("mount -t sysfs sysfs /sys\n")
            f.write("mount -t devtmpfs devtmpfs /dev\n")
            f.write("echo 'Booted successfully!'\n")
            f.write("exec /bin/bash\n")
        

        init.chmod(init.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)