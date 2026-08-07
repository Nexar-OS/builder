from pathlib import Path
from build import BuildContext
from recipe import TargetRecipe
from dataclasses import dataclass
from utils.logger import warn, info
from utils.file import merge_trees

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

        for recipe in self.recipes:
            recipe.build(ctx)
        
        return self

    def export(self, ctx: BuildContext) -> None:
        """
        Export all built recipe outputs into this stage's staging directory.

        For each recipe the install path is retrieved and its contents
        are merged into the stage directory.
        """
        info(f"Exporting to stage '{self.name}': {', '.join([ r.name for r in self.recipes ])}.")
        stage_dir = self._stage_dir(ctx)

        for recipe in self.recipes:
            path = recipe._install_path(ctx)
            
            if not path:
                warn(f"Failed to export recipe '{recipe.name}': No install path.")
                continue
            
            merge_trees(
                path,
                stage_dir,
                copy=False
            )