from concurrent.futures import (
    Future,
    ThreadPoolExecutor,
    wait,
    FIRST_COMPLETED
)

from .dependencies import DependencyGraph
from .recipe import BuildRecipe
from builder.utils.logger import info

class SequencerError(RuntimeError):
    """
    Thrown by the sequencer.
    """

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

        self._tasks: dict[str, BuildRecipe] = {}
        self._dependencies: dict[str, set[str]] = {}
        self._dependents: dict[str, set[str]] = {}

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
                self._tasks[recipe.name] = recipe
                self._dependencies[recipe.name] = set()
                self._dependents[recipe.name] = set()
        
        # Only BUILD edges become constraints.
        for node in self.build_graph.recipes:
            for dependency in self.build_graph.dependencies_of(node):
                self._dependencies[node].add(dependency)
                self._dependents[dependency].add(node)
    
    def _build(self, recipe: BuildRecipe) -> BuildRecipe:
        """
        Invokes the build of a recipe if it hasn't
        been built or is flagged as out-of-date.

        Args:
            recipe (BuildRecipe): The recipe to build.

        Returns:
            BuildRecipe: The recipe that has been built.
        """

        if recipe.needs_rebuild:
            info(f"Building recipe '{recipe.name}'...")
            recipe.build()
        else:
            info(f"Skipping recipe '{recipe.name}' (Up to date).")

        # TODO: error handling

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

        completed: set[str] = set()
        running: dict[Future[BuildRecipe], str] = {}
        result: list[BuildRecipe] = []

        with ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            while ready or running:
                # Fill all available worker slots
                while ready and len(running) < self.max_workers:
                    name = ready.pop()
                    task = self._tasks[name]

                    future = executor.submit(
                        self._build,
                        task,
                    )

                    running[future] = name
                
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
            unresolved = (
                set(self._tasks)
                - completed
            )

            raise SequencerError(
                "Could not schedule all recipes. "
                f"Unresolved: {sorted(unresolved)}"
            )

        return result