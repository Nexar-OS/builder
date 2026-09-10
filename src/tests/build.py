from tests.vars import ctx, max_workers

from builder.toolchain import load_or_build_cross_toolchain
from builder.stage import Stage

Stage.DEFAULT_MAX_WORKERS = max_workers
ctx.toolchain = load_or_build_cross_toolchain(ctx)

Stage.for_recipe(ctx, "core") \
    .build() \
    .export()