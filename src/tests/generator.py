# from tests.vars import ctx
from builder.recipe import *

gen = RecipeGenerator.github(
    repository="scop/bash-completion",
    filename="bash-completion-{version}.tar.xz"
).set("description", "Bash completion")

gen.latest_version()
gen._resolve_auto_hashes()

print(gen.schema)