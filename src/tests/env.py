from tests.vars import ctx

from builder.toolchain import load_or_build_cross_toolchain
from builder.build import *

ctx.toolchain = load_or_build_cross_toolchain(ctx)

exec = CommandRunner(
    ctx,
    default_profile=EnvironmentProfile.TARGET
)

print(exec.run([
    "echo", "hello"
]).stdout)