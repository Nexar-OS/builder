from concurrent.futures import (
    Future,
    ThreadPoolExecutor,
    wait,
    FIRST_COMPLETED
)

from dataclasses import dataclass

from .dependencies import DependencyGraph
from .recipe import (
    BuildRecipe,
    BuildRole,
)
from builder.utils.logger import info

class SequencerError(RuntimeError):
    """
    Thrown by the sequencer.
    """

@dataclass(frozen=True)
class RecipeKey:
    """
    A role dependent graph node of a recipe.

    This separation is needed, since a recipe could appear
    as both a BUILD as well as a RUNTIME dependency in the
    build Sequence.
    """

    name: str
    role: BuildRole

    @classmethod
    def get(cls, recipe: BuildRecipe):
        """
        Load a recipe key from a normal ``BuildRecipe`` instance.

        Args:
            recipe (BuildRecipe): The recipe.

        Returns:
            _type_: The key derived from that recipes name and build role.
        """
        return cls(recipe.name, recipe.build_role)

    def __repr__(self) -> str:
        return f"{self.name} ({self.role.name.upper()})"

class Sequencer:
    """
    Concurrently schedules recipes using dependency information.

    BUILD dependencies impose ordering constraints.

    RUNTIME dependencies only cause recipes to be included in the build
    plan.
    """

    def __init__(self,
                 build_graph: DependencyGraph | None,
                 runtime_graph: DependencyGraph | None,
                 max_workers: int = 1,
                ) -> None:

        self.build_graph = build_graph or DependencyGraph.empty()
        self.runtime_graph = runtime_graph or DependencyGraph.empty()

        self.max_workers = max_workers

        self._tasks: dict[RecipeKey, BuildRecipe] = {}
        self._dependencies: dict[RecipeKey, set[RecipeKey]] = {}
        self._dependents: dict[RecipeKey, set[RecipeKey]] = {}

        self._build_plan()

    def _build_plan(self) -> None:
        """
        Combines the BUILD and RUNTIME graphs into the set of recipes
        that need to be built.
        """

        # Initialize dependency and dependent mappings
        for graph in (
            self.build_graph,
            self.runtime_graph
        ):
            for recipe in graph.recipes.values():
                key = RecipeKey.get(recipe)
                self._tasks[key] = recipe
                self._dependencies[key] = set()
                self._dependents[key] = set()
        
        # Prevent recipes existing as both target and build dependencies
        # from being built as target before or concurrently as the build
        # role by making TARGET roles depend on SYSROOT roles.
        for task in self._tasks:
            name = task.name

            sysroot_key = RecipeKey(name, BuildRole.SYSROOT)
            target_key = RecipeKey(name, BuildRole.TARGET)


            if sysroot_key in self._tasks and target_key in self._tasks:
                self._dependencies[target_key].add(sysroot_key)
                self._dependents[sysroot_key].add(target_key)
    
        # Only BUILD edges become constraints.
        recipes = self.build_graph.recipes
        for recipe in recipes.values():
            node_key = RecipeKey.get(recipe)
            
            for dependency in self.build_graph.dependencies_of(recipe):
                dependency_recipe = recipes[dependency]
                dependency_key = RecipeKey.get(dependency_recipe)

                self._dependencies[node_key].add(dependency_key)
                self._dependents[dependency_key].add(node_key)
        
    def _build(self, recipe: BuildRecipe) -> BuildRecipe:
        """
        Invokes the build of a recipe if it hasn't
        been built or is flagged as out-of-date.

        Args:
            recipe (BuildRecipe): The recipe to build.

        Returns:
            BuildRecipe: The recipe that has been built.
        """

        recipe.build()
        return recipe
    
    def build(self) -> list[BuildRecipe]:
        """
        Build all recipes concurrently while respecting BUILD dependencies.

        Returns:
            list[BuildRecipe]: Recipes in the order in which they are completed.
        """

        # The number of unfinished prerequesites for every task/recipe.
        remaining = {
            name: len(dependencies)
            for name, dependencies in self._dependencies.items()
        }

        # The tasks/recipes that can concurrently be started.
        ready = [
            name
            for name, count in remaining.items()
            if count == 0
        ]

        completed: set[RecipeKey] = set()
        running: dict[Future[BuildRecipe], RecipeKey] = {}
        result: list[BuildRecipe] = []

        with ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            while ready or running:
                # Fill all available worker slots
                while ready and len(running) < self.max_workers:
                    key = ready.pop()
                    task = self._tasks[key]

                    future = executor.submit(
                        self._build,
                        task,
                    )

                    running[future] = key
                
                if not running:
                    break

                # Wait until at least one recipe finishes
                finished, _ = wait(
                    running,
                    return_when=FIRST_COMPLETED
                )

                for future in finished:
                    name = running.pop(future)
                    recipe = future.result()

                    completed.add(name)
                    result.append(recipe)

                    # Every dependent potentially became runnable
                    for dependent in self._dependents[name]:
                        remaining[dependent] -= 1

                        if remaining[dependent] == 0:
                            ready.append(dependent)
        
        if len(completed) != len(self._tasks):
            unresolved = [ key.__repr__() for key in (
                set(self._tasks)
                - completed
            )]

            raise SequencerError(
                "Could not schedule all recipes. "
                f"Unresolved: {sorted(unresolved)}"
            )

        return result