from pathlib import Path
from builder.recipe.loader import *
from builder.recipe import BuildRole



file = Path(__file__).parent / "mockup_recipe.yaml"

schema = load_schema(file)
recipe = load_recipe_from_schema(BuildRole.TARGET, schema)
print(recipe.build_system)