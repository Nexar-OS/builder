from tests.vars import ctx

from builder.build.system import *
from pathlib import Path
from builder.recipe import *
from builder.recipe.target import *

def load_recipes():
    import importlib
    import pkgutil
    import inspect

    recipes = []

    package = importlib.import_module("builder.recipe.target")

    for module_info in pkgutil.iter_modules(package.__path__):
        if module_info.ispkg:
            continue

        module = importlib.import_module(f"{package.__name__}.{module_info.name}")

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                    name.endswith("Recipe")
                    and obj is not BuildRecipe
                    and issubclass(obj, TargetRecipe)
                    and obj.__module__ == module.__name__
                ):
                recipes.append(obj(ctx))
    
    return recipes

existing_recipes = [
    f.name.removesuffix(".yaml")
    for f in Path("src/recipe/").iterdir()
    if f.is_file() and f.name.endswith(".yaml")
]

recipes = load_recipes()
recipes = [ r for r in recipes if not r.name in existing_recipes ]

dst = Path("build/exported_recipes/")
dst.mkdir(exist_ok=True, parents=True)

preset = Path("src/recipe/.example").read_text()

def _is_overridden(recipe: TargetRecipe, method: str) -> bool:
    return getattr(type(recipe), method) is not getattr(TargetRecipe, method)

def export_recipe(recipe: TargetRecipe) -> str | None:
    if not any(isinstance(recipe.build_system, c) for c in [
        Autotools,
        CMake,
        Meson
    ]):
        return None
    
    if not recipe.build_system:
        return None

    config_args = (recipe.build_system.config_args or []) + recipe._config_args(ctx)
    config_args = [ arg for arg in config_args if not any(arg.startswith(x) for x in [ "--host", "--build", "--target", "--sysroot" ]) ]
    config_args = "\n      - ".join(config_args) + "\n"


    build_args = recipe.build_system.build_args or []
    build_args = "\n      - ".join(build_args) + "\n"

    install_args = recipe.build_system.install_args or []
    install_args = "\n      - ".join(install_args) + "\n"

    python_notice = "See in python code!"
    patches = python_notice if _is_overridden(recipe, "patch") else "<patches>"
    post_install = python_notice if _is_overridden(recipe, "post_install") else "<post_install>"
    prepare = python_notice if _is_overridden(recipe, "prepare") else "<prepare>"

    return preset \
        .replace("<name>", recipe.name) \
        .replace("<version>", recipe.version) \
        .replace("<source_type>", type(recipe.sources[0]).__name__.lower().removesuffix('source')) \
        .replace("<source_url>", recipe.sources[0].url.replace(recipe.version, '${version}')) \
        .replace("<source_name>", recipe.sources[0].name) \
        .replace("<source_hash>", getattr(recipe.sources[0], 'md5hash')) \
        .replace("<config_args>", config_args) \
        .replace("<build_args>", build_args) \
        .replace("<install_args>", install_args) \
        .replace("<build_method>", recipe.build_method.name) \
        .replace("<build_system>", type(recipe.build_system).__name__.lower()) \
        .replace("<disable_fakeroot>", f"{getattr(recipe.build_system, 'disable_fakeroot', False)}") \
        .replace("<patches>", patches) \
        .replace("<post_install>", post_install) \
        .replace("<prepare>", prepare) \
        .replace("disable_fakeroot: False\n", "") \
        .replace("config_args:\n      - \n", "config_args:") \
        .replace("build_args:\n      - \n", "build_args:") \
        .replace("install_args:\n      - \n", "install_args:") \
        .replace("\n  prepare: |\n    <prepare>\n", "") \
        .replace("\n  patches:\n    - <patches>\n", "")


for r in recipes:
    path: Path = dst / (r.name + ".yaml")
    exported = export_recipe(r)

    if not exported:
        print(f"[WARNING]: Failed to export '{r.name}'")
        continue

    path.write_text(exported)