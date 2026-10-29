from tests.vars import ctx

from builder.toolchain import load_or_build_cross_toolchain
from builder.build import *

ctx.toolchain = load_or_build_cross_toolchain(ctx)

exec = Shell(
    environment=Environment.from_context(
        ctx=ctx,
        profile=EnvironmentProfile.TARGET
    ),
    persistent=True
)

exec.run("export VAR1=hey")

print(
    exec.run(
        "echo var value=$VAR1"
    ).stdout
)