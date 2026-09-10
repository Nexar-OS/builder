from tests.vars import ctx
from builder.recipe import BuildRole

recipes = [
    ctx.registry.getOrThrow(
        name=recipe,
        role=BuildRole.TARGET,
        ctx=ctx
    )
    for recipe in sorted(ctx.registry.paths().keys())
]

for recipe in recipes:
    version_source = recipe.version_source
    
    print(f"Loading: {recipe.name}")
    version = version_source.latest_version if version_source else None
    print(f"Recipe '{recipe.name}': {version or '/'}")