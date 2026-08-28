from builder.recipe import *
from .vars import ctx

recipe = GenericRecipe(
    BuildRole.TARGET,
    name="mockup",
    version="1.0.0",
    sources=[

    ]
)

recipe.build(ctx)