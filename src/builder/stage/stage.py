from typing import Callable
from pathlib import Path
from builder.build import BuildContext
from builder.recipe import TargetRecipe, BuildRecipe
from dataclasses import dataclass
from builder.utils.logger import warn, info
from builder.utils.file import merge_trees

@dataclass
class Stage:
    """
    Represents a build stage that groups multiple target recipes
    under a common staging directory.

    A stage is responsible for building all associated recipes and
    exporting their installed outputs into a dedicated staging area.

    Attributes:
        name (str): Name of the stage and its staging directory
        recipes (list[TargetRecipe]): Recipes included in this stage
    """
    name: str
    recipes: list[TargetRecipe]

    # Optional lifecycle hooks
    pre_build_hook: Callable | None = None
    post_build_hook: Callable | None = None

    def _stage_dir(self, ctx: BuildContext) -> Path:
        """
        Return the directory used to store this stage's exported files
        """

        dir = ctx.staging_dir / self.name
        dir.mkdir(exist_ok=True, parents=True)
        return dir

    def build(self, ctx: BuildContext) -> "Stage":
        """
        Build all recipes associated with this stage.

        Each recipe's ``build`` method is invoked sequentially using
        the provided build context

        Args:
            ctx (BuildContext): Context used for the build.
        """

        if self.pre_build_hook:
            self.pre_build_hook(self, ctx)

        for recipe in self.recipes:
            if recipe.needs_rebuild:
                info(f"Building '{recipe.name}'.")
                recipe.build()
            
            else:
                info(f"Skipping {recipe.name} (up to date).")
        
        if self.post_build_hook:
            self.post_build_hook(self, ctx)

        return self

    def _export_recipe(self, ctx: BuildContext, recipe: TargetRecipe, stage_dir: Path, copy: bool = False):
        """
        Exports a specific recipe to the target stage.
        """
        # Export dependencies
        deps = getattr(recipe, "depends_on", [])
        if deps:
            info(f"Exporting dependencies of '{recipe.name}'")
            
            for dep in deps:
                info(f" | Exporting '{dep.name}'")
                self._export_recipe(ctx, dep, stage_dir, copy)

        # Export package

        path = recipe._install_path
        
        if not path:
            warn(f"Failed to export recipe '{recipe.name}': No install path.")
            return

        merge_trees(
            path,
            stage_dir,
            copy=copy
        )

    def export(self, ctx: BuildContext, copy: bool = False) -> None:
        """
        Export all built recipe outputs into this stage's staging directory.

        For each recipe the install path is retrieved and its contents
        are merged into the stage directory.

        Args:
            copy (bool): If true, separate root filesystems will be kept.
        """
        info(f"Exporting to stage '{self.name}': {', '.join([ r.name for r in self.recipes ])}.")
        stage_dir = self._stage_dir(ctx)

        for recipe in self.recipes:
            self._export_recipe(ctx, recipe, stage_dir, copy)