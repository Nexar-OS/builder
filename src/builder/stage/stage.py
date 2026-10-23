from pathlib import Path
from typing import Callable, ClassVar
from dataclasses import dataclass

from builder.utils.logger import warn, info
from builder.utils.file import merge_trees, rmtree
from builder.build import BuildContext
from builder.recipe import (
    BuildRecipe,
    BuildRole,
    RecipeKey,
    DependencyGraph,
    DependencyKind,
    Sequencer,
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
        add_optional_dependencies (bool): When set to ``True``, optional runtime dependencies will be built as well.
        ignore_dependency_errors (bool): When set to ``True``, missing dependencies will be tollerated.
        max_retries (int): The maximum amount to retry building each recipe if it fails.
        throw_on_fail (bool): Make the sequencer throw a ``RuntimeError`` if a recipe cannot be built.
        pre_build_hook (Callable[BuildContext]): An optional pre-build hook.
        post_build_hook (Callable[BuildContext]): An optional post-build hook.
    """

    ctx: BuildContext

    name: str

    recipes: list[str]
    build_role: BuildRole = BuildRole.TARGET
    add_runtime_dependencies: bool = False
    add_optional_dependencies: bool = False
    ignore_dependency_errors: bool = False
    max_retries: int = 3
    throw_on_fail: bool = False
    max_workers: int | None = None

    pre_build_hook: Callable | None = None
    post_build_hook: Callable | None = None

    DEFAULT_MAX_WORKERS: ClassVar[int] = 1

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
        registry = self.ctx.registry

        # Start with user-selected recipes.
        recipes: dict[RecipeKey, BuildRecipe] = {
            RecipeKey.get(recipe): recipe
            for recipe in self._recipes
        }

        # Initialize optional dependency graphs.
        self.runtime_dependencies = None
        self.optional_dependencies = None

        # Every resolved dependency of one graph might also introduce
        # new dependencies on another (or the same) graph. We therefore
        # loop over the whole process of discovering dependencies until
        # nothing changes any longer.
        while True:
            previous = set(recipes)

            # Add runtime dependencies
            if self.add_runtime_dependencies:
                self.runtime_dependencies = DependencyGraph(
                    recipes=recipes.values(),
                    registry=registry,
                    kind=DependencyKind.RUNTIME,
                    allow_cycles=True,
                    ignore_dependency_errors=self.ignore_dependency_errors,
                )

                recipes.update(self.runtime_dependencies.recipes)
            
            # Add optional runtime dependencies
            if self.add_optional_dependencies:
                self.optional_dependencies = DependencyGraph(
                    recipes=recipes.values(),
                    registry=registry,
                    kind=DependencyKind.OPTIONAL,
                    allow_cycles=True,
                    ignore_dependency_errors=self.ignore_dependency_errors,
                )

                recipes.update(self.optional_dependencies.recipes)
            
            # Host dependencies
            self.host_dependencies = DependencyGraph(
                recipes=recipes.values(),
                registry=registry,
                kind=DependencyKind.HOST,
                allow_cycles=False,
                ignore_dependency_errors=self.ignore_dependency_errors,
            )
            recipes.update(self.host_dependencies.recipes)

            # Build dependencies
            self.build_dependencies = DependencyGraph(
                recipes=recipes.values(),
                registry=registry,
                kind=DependencyKind.BUILD,
                allow_cycles=False,
                ignore_dependency_errors=self.ignore_dependency_errors,
            )
            recipes.update(self.build_dependencies.recipes)
            
            # Stop when no graph discovered any additional recipes.
            if set(recipes) == previous:
                break

    def __post_init__(self):
        self._load_recipes()
        self._build_dependency_graphs()

        graphs = []
        if self.runtime_dependencies:
            graphs.append(self.runtime_dependencies)
        
        if self.optional_dependencies:
            graphs.append(self.optional_dependencies)

        self.sequencer = Sequencer(
            graphs=graphs,
            constraining_graphs=[
                self.build_dependencies,
                self.host_dependencies
            ],
            max_workers=self.max_workers or Stage.DEFAULT_MAX_WORKERS
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
        info(f"Exporting recipe '{recipe.name}' to '{str(stage_dir)}'")

        path = recipe._dest_dir
        
        if not path:
            warn(f"Failed to export recipe '{recipe.name}': No install path.")
            return

        merge_trees(
            path,
            stage_dir,
            copy=copy
        )
    
    @classmethod
    def for_recipe(cls, ctx: BuildContext, recipe: str, max_workers: int | None = None, **kwargs) -> "Stage":
        """
        Construct a stage for just one recipe and its runtime dependencies.

        Args:
            ctx (BuildContext): The context used for building.
            recipe (str): The recipe to build.
            max_workers (int): The maximum workers amount. (Defaults to ``Stage.DEFAULT_MAX_WORKERS``).

        Returns:
            Stage: A stage for this recipe and its dependencies.
        """
        return cls(
            ctx=ctx,
            name=recipe,
            recipes=[ recipe ],
            add_runtime_dependencies=True,
            max_workers=max_workers or Stage.DEFAULT_MAX_WORKERS,
            **kwargs
        )

    def export(self, copy: bool = True) -> "Stage":
        """
        Exports all recipes of this stage into a shared stage-dir.
        """
        out = self._dir

        # Clean root
        if out.is_dir():
            warn(f"Stage root '{out}' already existed. Removing...")
            rmtree(out)

        recipes = self._recipes

        # Export runtime dependencies if flag is enabled
        if self.add_runtime_dependencies and self.runtime_dependencies:
            recipes.extend(
                list(self.runtime_dependencies.recipes.values())
            )

        # Rootfs recipe should always be exported first (if present)
        recipes = sorted(recipes, key=lambda r: r.name != "rootfs")

        for recipe in recipes:
            self._export_recipe(recipe, out, copy)
        
        return self

    def build(self) -> "Stage":
        """
        Build all recipes associated with this stage.

        Each recipe's ``build`` method is invoked sequentially using
        the provided build context
        """

        self.sequencer.build(
            max_retries=self.max_retries,
            throw_on_fail=self.throw_on_fail
        )
        return self