from pathlib import Path
from builder.recipe.loader import *
from builder.recipe import BuildRole



file = Path(__file__).parent / "mockup_recipe.yaml"

recipe = load_recipe(file, BuildRole.TARGET)
assert recipe
print(recipe.build_system)