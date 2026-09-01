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
    Directed dependency graph for a collection of recipes.
    Resolves the dependency closure for a single dependency kind.
    """
    def __init__(self,
                 recipes: Iterable[BuildRecipe],
                 registry: RecipeRegistry,
                 kind: DependencyKind,
                 allow_cycles: bool = False,
                ) -> None:
        self.registry = registry
        self.kind = kind
        self.allow_cycles = allow_cycles

        self._recipes: dict[str, BuildRecipe] = {}

        self._dependents: dict[str, set[str]] = {}
        self._dependencies: dict[str, set[str]] = {}

        self._resolved: set[str] = set()
        self._resolving: set[str] = set()

        for recipe in recipes:
            self._resolve(recipe)

    def _load_dependency(self, name: str, parent: BuildRecipe) -> BuildRecipe:
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
            role=self.kind.build_role,
            ctx=parent.ctx
        )

        if not dependency:
            raise RuntimeError(
                f"Recipe '{parent.name}' depends on '{name}', "
                f"but recipe '{name}' could not be loaded."
            )
        
        return dependency

    def _dependency_names(self, recipe: BuildRecipe) -> Iterable[str]:
        """
        Return the dependencies relevant to this graph.
        """
        match self.kind:
            case DependencyKind.BUILD:
                yield from recipe.dependencies.build or []
            
            case DependencyKind.RUNTIME:
                yield from recipe.dependencies.required or []
        
            case _:
                raise ValueError(f"Unhandled dependency kind: '{self.kind!r}'")

    def _resolve(self, recipe: BuildRecipe):
        """
        Recursively resolve a recipe and all of its dependencies.

        Args:
            recipe (BuildRecipe): The recipe to resolve.
            kind (DependencyKind): The kind of dependencies to resolve.
        """
        if recipe.name in self._resolved:
            return
        
        if recipe.name in self._resolving:
            # Ignore cycles if allowed
            if self.allow_cycles:
                return
            
            raise DependencyCycleError(
                f"Dependency cycle involving '{recipe.name}'."
            )
        
        self._resolving.add(recipe.name)

        self._recipes[recipe.name] = recipe
        self._dependencies.setdefault(recipe.name, set())
        self._dependents.setdefault(recipe.name, set())
        
        for name in self._dependency_names(recipe):
            dependency = self._load_dependency(name, recipe)

            self._dependencies[recipe.name].add(dependency.name)
            self._dependents.setdefault(dependency.name, set())
            self._dependents[dependency.name].add(recipe.name)
            
            self._resolve(dependency)
        
        self._resolving.remove(recipe.name)
        self._resolved.add(recipe.name)
    
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

    def dependents_of(self, recipe: str | BuildRecipe) -> set[str]:
        """
        Returns a list of all dependents of a recipe.

        Args:
            recipe (str | BuildRecipe): The recipe to check.
        """

        name = recipe if isinstance(recipe, str) else recipe.name
        return set(self._dependents[name])


    @property
    def topological_order(self) -> list[BuildRecipe]:
        """
        Returns recipes in a valid dependency order.
        """

        remaining = {
            node: len(dependencies)
            for node, dependencies in self._dependencies.items()
        }

        ready = list(
            node
            for node, count in remaining.items()
            if count == 0
        )

        result: list[BuildRecipe] = []

        while ready:
            node = ready.pop(0)
            result.append(self._recipes[node])

            for dependent in self._dependents.get(node, ()):
                remaining[dependent] -= 1

                if remaining[dependent] == 0:
                    ready.append(dependent)

        return result