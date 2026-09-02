from pathlib import Path
from .recipe import (
    GenericRecipe,
    BuildRole,
)
from builder.build import BuildContext
from .loader import load_recipe
from builder.utils.logger import warn, debug

class RecipeNotFoundError(RuntimeError):
    """
    Thrown when a recipe couldn't be resolved.
    """

class RecipeRegistry:
    """
    Interface for discovering and lazy loading recipes
    identified by their unique recipe name.
    """

    def __init__(self, recipe_dirs: list[Path]) -> None:
        self.recipe_dirs = recipe_dirs

        self._paths: dict[str, Path] = self.discover()
        self._loaded: dict[tuple[str, BuildRole], GenericRecipe] = {}

    def paths(self) -> dict[str, Path]:
        """
        Returns the cached recipe paths.

        Returns:
            dict[str, Path]: A mapping of recipe names to their declaration file path.
        """        
        return dict(self._paths)

    def discover(self) -> dict[str, Path]:
        """
        Discover all recipe files without loading them.
        """
        loaded = {}

        for directory in self.recipe_dirs:
            for path in directory.rglob("*.yaml"):
                name = path.stem

                if name in loaded:
                    warn(
                        f"Multiple recipes found with same filename ('{name}'): "
                        f"'{loaded[name]}' and '{path}'!"
                        f" Skipping '{path}'..."
                    )
                    continue

                loaded[name] = path
        
        return loaded
    
    def get(self, name: str, role: BuildRole, ctx: BuildContext) -> GenericRecipe | None:
        """
        Loads and instantiates a recipe from its name.

        Recipes are cached after their first load.

        Args:
            name (str): The name of the recipe.
            role (BuildRole): The role the recipe will be used for.
            ctx (BuildContext): The context that will be used to build the recipe with.

        Returns:
            GenericRecipe | None: Returns the loaded or cached recipe.
                                  Or None if recipe couldn't be loaded.
        """

        if name not in self._paths:
            warn(f"Failed to load recipe '{name}'."
                 f"(Searched paths: {', '.join([ str(x) for x in self.recipe_dirs])})"
                )
            return None
        
        key = (name, role)

        if key not in self._loaded:
            recipe = load_recipe(
                recipe_path=self._paths[name],
                role=role,
                ctx=ctx
            )

            if not recipe:
                return None

            self._loaded[key] = recipe
        else:
            debug(f"Using cached recipe for '{name} ({role.name})'")

        return self._loaded[key]

    def getOrThrow(self, name: str, role: BuildRole, ctx: BuildContext) -> GenericRecipe:
        """
        Loads and instantiates a recipe from its name.

        If the recipe doesn't exist or couldn't be parsed,
        a "RecipeNotFoundError" will be thrown.

        Args:
            name (str): The name of the recipe.
            role (BuildRole): The role the recipe will be used for.
            ctx (BuildContext): The context that will be used to build the recipe with.
        """

        recipe = self.get(name, role, ctx)

        if not recipe:
            raise RecipeNotFoundError(f"Failed to locate recipe '{name}'.")

        return recipe

    def path(self, name: str) -> Path | None:
        """
        Return the path to the recipe file without loading the recipe itself.

        Args:
            name (str): The name of the recipe to find.
 
        Returns:
            Path | None: Returns the path of the recipe.
                  None if not found.
        """
        return self._paths[name]
    
    def cached(self, name: str, role: BuildRole) -> GenericRecipe | None:
        """
        Returns the cached value for a recipe with a certain name.

        Args:
            name (str): The name of the recipe to search for.
            role (BuildRole): The build role of the recipe

        Returns:
            GenericRecipe | None: Returns either the recipe or None if none was cached.
        """
        return self._loaded[(name, role)]