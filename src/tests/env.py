from tests.vars import ctx

from builder.toolchain import load_or_build_cross_toolchain
from builder.build import *

ctx.toolchain = load_or_build_cross_toolchain(ctx)

with Shell(
    environment=Environment.from_context(
        ctx=ctx,
        profile=EnvironmentProfile.TARGET
    ),
    persistent=True
) as shell:
    shell.run("export VAR1=hey")
    print("Shell output: " + shell.run("echo $VAR1").stdout.strip())