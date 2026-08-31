from typing import Callable
from dataclasses import dataclass

from builder.utils.logger import warn, info
from builder.build import BuildContext
from builder.recipe import (
    BuildRecipe,
    BuildRole,
    RecipeRegistry,
    DependencyGraph,
    DependencyKind
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
        registry (RecipeRegistry): The registry to load recipes from.
        name (str): Name of the stage.
        recipes (list[str]): Recipes included in this stage.
        build_role (BuildRole): The role in which recipes should be built.
        add_runtime_dependencies (bool): When set to ``True``, runtime dependencies will be built as well.
        pre_build_hook (Callable[BuildContext]): An optional pre-build hook.
        post_build_hook (Callable[BuildContext]): An optional post-build hook.
    """

    ctx: BuildContext
    registry: RecipeRegistry

    name: str

    recipes: list[str]
    build_role: BuildRole = BuildRole.TARGET
    add_runtime_dependencies: bool = False

    pre_build_hook: Callable | None = None
    post_build_hook: Callable | None = None

    def _load_recipes(self):
        """
        Loads/instantiates all recipes from their names.
        """
        self._recipes: list[BuildRecipe] = []

        for recipe in self.recipes:
            loaded = self.registry.get(
                name=recipe,
                role=self.build_role,
                ctx=self.ctx
            )

            if not loaded:
                warn(f"Failed to load recipe '{recipe}'!")
                continue

            self._recipes.append(loaded)

    def _build_dependency_graph(self):
        """
        Constructs the dependency graph.
        """
        kinds = [ DependencyKind.BUILD ]
        if self.add_runtime_dependencies:
            kinds.append(DependencyKind.RUNTIME)

        self._dependency_graph: DependencyGraph = DependencyGraph(
            recipes=self._recipes,
            registry=self.registry,
            kinds=kinds
        )

    def __post_init__(self):
        self._load_recipes()
        self._build_dependency_graph()

        self._recipes = self._dependency_graph.topological_order + self._recipes

    def build(self):
        """
        Build all recipes associated with this stage.

        Each recipe's ``build`` method is invoked sequentially using
        the provided build context
        """

        if self.pre_build_hook:
            self.pre_build_hook(self, self.ctx)

        for recipe in self._recipes:
            if recipe.needs_rebuild:
                info(f"Building '{recipe.name}'.")
                recipe.build()
            
            else:
                info(f"Skipping {recipe.name} (up to date).")
        
        if self.post_build_hook:
            self.post_build_hook(self, self.ctx)

        return self