from tests.vars import ctx
from builder.recipe import BuildRole

recipe = ctx.registry.getOrThrow("version_source_test", BuildRole.TARGET, ctx)

source = recipe.version_source
assert source

print(
    "Latest upstream version: " +
    max(source.versions).raw
)

for version in source.versions:
    print(version)