from __future__ import annotations

from typing import Iterable, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum, auto

if TYPE_CHECKING:
    from .recipe import BuildRecipe, BuildRole
    from .registry import RecipeRegistry

@dataclass
class Dependencies:
    """
    Describes the dependencies required to build and use a recipe.

    Attributes:
        required: Dependencies required at runtime.
        optional: Dependencies that may be used but are not required.
        build: Dependnecies required (only) during the build process.
    """

    required: list[str] | None = None
    optional: list[str] | None = None
    build: list[str] | None = None
    
    @classmethod
    def none(cls):
        """
        Create an empty dependency declaration.

        Returns:
            Dependency: A Dependencies instance with all dependency lists empty.
        """
        return Dependencies(
            required=[],
            optional=[],
            build=[],
        )

class DependencyKind(Enum):
    RUNTIME = auto()
    """
    Dependencies only needed at runtime.
    """

    BUILD = auto()
    """
    Dependencies needed to build a recipe.
    """

    @property
    def build_role(self) -> "BuildRole":
        """
        Returns the appropriate build role for recipes
        matching this dependency kind.

        Returns:
            BuildRole: The build role.
        """
        from .recipe import BuildRole

        match self:
            case DependencyKind.RUNTIME:
                return BuildRole.TARGET
            
            case DependencyKind.BUILD:
                return BuildRole.SYSROOT

class DependencyCycleError(RuntimeError):
    """
    Thrown on circular dependencies.
    """

class DependencyGraph():
    """
    A directed acyclic graph describing build or runtime dependencies between multiple recipes.

    e.g. ``A -> B`` means ``B depends on A``.
    Therefore A must be built before B.
    """
    def __init__(self,
                 recipes: Iterable[BuildRecipe],
                 registry: RecipeRegistry,
                 kinds: list[DependencyKind],
                ) -> None:
        self.registry = registry
        self.kinds = kinds

        self._recipes: dict[str, BuildRecipe] = {}

        # Recipes which are dependencies of another recipe.
        self._dependencies: dict[str, set] = {}

        # Reverse edges:
        # dependency -> recipes depending on it
        self._dependents: dict[str, set] = {}

        self._build_graph(recipes)

    def _build_graph(self, recipes: Iterable[BuildRecipe]):
        """
        Builds the dependency graph and checks for circular dependencies.
        """
        for recipe in recipes:
            if recipe.name in self._recipes:
                continue
            for kind in self.kinds:
                self._resolve(recipe, kind)
        
        self._check_cycles()

    def _load_dependency(self, name: str, parent: BuildRecipe, kind: DependencyKind) -> BuildRecipe:
        """
        Resolve a dependency through the registry.

        Args:
            name (str): The name of the dependency to resolve.
            parent (BuildRecipe): The parent recipe that requires it.

        Returns:
            BuildRecipe: The loaded dependency.
        """

        dependency = self.registry.get(
            name=name,
            role=kind.build_role,
            ctx=parent.ctx
        )

        if not dependency:
            raise RuntimeError(
                f"Recipe '{parent.name}' depends on '{name}', "
                f"but recipe '{name}' could not be loaded."
            )
        
        return dependency

    def _dependency_names(self, recipe: BuildRecipe, kind: DependencyKind) -> list[str]:
        """
        Return the dependencies relevant to this graph.
        """
        match kind:
            case DependencyKind.BUILD:
                return list(recipe.dependencies.build or [])
            
            case DependencyKind.RUNTIME:
                return list(recipe.dependencies.required or [])

    def _resolve(self, recipe: BuildRecipe, kind: DependencyKind):
        """
        Recursively resolve a recipe and all of its dependencies.

        Args:
            recipe (BuildRecipe): The recipe to resolve.
            kind (DependencyKind): The kind of dependencies to resolve.
        """
        
        self._recipes[recipe.name] = recipe
        self._dependencies[recipe.name] = set()
        self._dependents.setdefault(recipe.name, set())
        
        for name in self._dependency_names(recipe, kind):
            dependency = self._load_dependency(name, recipe, kind)

            self._dependencies[recipe.name].add(dependency.name)
            self._dependents \
                .setdefault(dependency.name, set()) \
                .add(recipe.name)
            
            self._resolve(dependency, kind)
    
    def _check_cycles(self) -> None:
        """
        Check the graph for dependency cycles.
        """

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(name: str) -> None:
            if name in visiting:
                raise DependencyCycleError(f"Dependency cycle involving '{name}'.")
            
            if name in visited:
                return
            
            visiting.add(name)

            for dependency in self._dependencies[name]:
                visit(dependency)
            
            visiting.remove(name)
            visited.add(name)
        
        for name in self._recipes:
            visit(name)
    
    @property
    def recipes(self) -> dict[str, BuildRecipe]:
        """
        Returns all recipes contained in the resolved graph.
        """
        return dict(self._recipes)
    
    def dependencies_of(self, recipe: str | BuildRecipe) -> set[str]:
        """
        Returns a list of all dependencies of a recipe.

        Args:
            recipe (str | BuildRecipe): The recipe to check.
        """

        name = recipe if isinstance(recipe, str) else recipe.name
        return set(self._dependencies[name])

    @property
    def topological_order(self) -> list[BuildRecipe]:
        """
        Returns recipes in a valid dependency order.
        """

        remaining = {
            name: len(dependencies)
            for name, dependencies in self._dependencies.items()
        }

        ready = sorted(
            name
            for name, count in remaining.items()
            if count == 0
        )

        result: list[BuildRecipe] = []

        while ready:
            name = ready.pop(0)
            result.append(self._recipes[name])

            for dependent in sorted(self._dependents.get(name, ())):
                remaining[dependent] -= 1

                if remaining[dependent] == 0:
                    ready.append(dependent)
                
            ready.sort()

        if len(result) > len(self._recipes):
            raise DependencyCycleError("Dependency graph contains a cycle.")

        return result