from pathlib import Path
from typing import Callable
from dataclasses import dataclass

from builder.utils.logger import warn, info
from builder.utils.file import merge_trees
from builder.build import BuildContext
from builder.recipe import (
    BuildRecipe,
    BuildRole,
    DependencyGraph,
    DependencyKind,
    Sequencer
)

@dataclass
class Stage:
    """
    Represents a build stage that groups multiple recipes
    under a common staging directory.

    A stage is responsible for building all associated recipes and dependencies
    and building them properly.

    Attributes:
        ctx (BuildContext): The context used for building recipes in this stage.
        name (str): Name of the stage.
        recipes (list[str]): Recipes included in this stage.
        build_role (BuildRole): The role in which recipes should be built.
        add_runtime_dependencies (bool): When set to ``True``, runtime dependencies will be built as well.
        ignore_dependency_errors (bool): When set to ``True``, missing dependencies will be tollerated.
        pre_build_hook (Callable[BuildContext]): An optional pre-build hook.
        post_build_hook (Callable[BuildContext]): An optional post-build hook.
    """

    ctx: BuildContext

    name: str

    recipes: list[str]
    build_role: BuildRole = BuildRole.TARGET
    add_runtime_dependencies: bool = False
    ignore_dependency_errors: bool = False

    pre_build_hook: Callable | None = None
    post_build_hook: Callable | None = None

    def _load_recipes(self):
        """
        Loads/instantiates all recipes from their names.
        """
        self._recipes: list[BuildRecipe] = []

        for recipe in self.recipes:
            loaded = self.ctx.registry.get(
                name=recipe,
                role=self.build_role,
                ctx=self.ctx
            )

            if not loaded:
                warn(f"Failed to load recipe '{recipe}'!")
                continue

            self._recipes.append(loaded)

    def _build_dependency_graphs(self):
        """
        Constructs the dependency graphs.
        """
        self._build_dependencies = DependencyGraph(
            recipes=self._recipes,
            registry=self.ctx.registry,
            kind=DependencyKind.BUILD,
            allow_cycles=False,
            ignore_dependency_errors=self.ignore_dependency_errors
        )

        self.runtime_dependencies = None
        if self.add_runtime_dependencies:
            self.runtime_dependencies = DependencyGraph(
                recipes=self._recipes,
                registry=self.ctx.registry,
                kind=DependencyKind.RUNTIME,
                allow_cycles=True,
                ignore_dependency_errors=self.ignore_dependency_errors
            )

    def __post_init__(self):
        self._load_recipes()
        self._build_dependency_graphs()

        self.sequencer = Sequencer(
            build_graph=self._build_dependencies,
            runtime_graph=self.runtime_dependencies,
            max_workers=16
        )
    
    @property
    def _dir(self) -> Path:
        """
        Returns the shared stage root for this stage.
        """
        dir = self.ctx.staging_dir / self.name
        dir.mkdir(exist_ok=True, parents=True)
        return dir

    def _export_recipe(self, recipe: BuildRecipe, stage_dir: Path, copy: bool = False) -> None:
        """
        Exports a specific recipe to the target stage.
        """
        
        path = recipe._install_path
        
        if not path:
            warn(f"Failed to export recipe '{recipe.name}': No install path.")
            return

        merge_trees(
            path,
            stage_dir,
            copy=copy
        )

    def export(self) -> None:
        """
        Exports all recipes of this stage into a shared stage-dir.
        """
        out = self._dir
        for recipe in self._recipes:
            info(f"Exporting recipe '{recipe.name}' to '{str(out)}'")
            self._export_recipe(recipe, out)
        

    def build(self) -> list[BuildRecipe]:
        """
        Build all recipes associated with this stage.

        Each recipe's ``build`` method is invoked sequentially using
        the provided build context
        """

        return self.sequencer.build()