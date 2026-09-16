from pathlib import Path
from dataclasses import dataclass
from builder.recipe import *

@dataclass
class Package:
    """
    Represents a completely built recipe.

    A Package combines package metadata with the filesystem tree produced
    by the build output of one recipe.

    Attributes:
        metadata (RecipeMetadata): The metadata describing this package.
        rootfs (Path): Filesystem contents belonging to the package.
    """

    metadata: RecipeMetadata
    rootfs: Path

    @classmethod
    def from_recipe(cls, recipe: BuildRecipe) -> "Package | None":
        """
        Create a package abstraction from a recipe.

        Only recipes of type ``BuildRole.TARGET`` are valid!

        If the recipe has yet to be built, the function will exit without
        returning a valid package.

        Args:
            recipe (BuildRecipe): The recipe to use.

        Returns:
            Package | None: The package derived from the recipe.
                            None if the recipe hasn't been built yet or is not a ``TARGET`` package.
        """
        # Only target packages get their own rootfs
        if recipe.build_role != BuildRole.TARGET:
            return None

        # Assume rebuild needed means the recipe
        # hasn't been built yet.
        if recipe.needs_rebuild:
            return None

        # Need to ensure rootfs actually exists
        rootfs = recipe._dest_dir
        if not rootfs or not rootfs.is_dir():
            return None

        return cls(
            metadata=recipe.metadata,
            rootfs=rootfs
        )