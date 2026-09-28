# from tests.vars import ctx
from builder.recipe import *

gen = RecipeGenerator.base(name="test")
gen.add_tarball(
    url="https://download-mirror.savannah.gnu.org/releases/attr/attr-2.6.0.tar.xz",
    md5hash="auto"
)

print(gen.schema)