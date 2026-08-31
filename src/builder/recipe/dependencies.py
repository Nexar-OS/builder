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

@dataclass(frozen=True, slots=True)
class DependencyNode:
    name: str
    kind: DependencyKind

    @property
    def role(self) -> "BuildRole":
        return self.kind.build_role

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

        self._recipes: dict[DependencyNode, BuildRecipe] = {}
        self._resolved: set[DependencyNode] = set()
        self._resolving: set[DependencyNode] = set()

        # Recipes which are dependencies of another recipe.
        self._dependencies: dict[DependencyNode, set[DependencyNode]] = {}

        # Reverse edges:
        # dependency -> recipes depending on it
        self._dependents: dict[DependencyNode, set[DependencyNode]] = {}

        self._build_graph(recipes)

    def _build_graph(self, recipes: Iterable[BuildRecipe]):
        """
        Builds the dependency graph and checks for circular dependencies.
        """
        for recipe in recipes:
            for kind in self.kinds:
                self._resolve(recipe, kind)

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
        
        node = DependencyNode(recipe.name, kind)

        if node in self._resolved:
            return
        
        if node in self._resolving:
            # Runtime dependency cycles are allowed
            if kind == DependencyKind.RUNTIME:
                return
            
            raise DependencyCycleError(
                f"Dependency cycle involving '{recipe.name}'."
            )
        
        self._resolving.add(node)

        self._recipes[node] = recipe
        self._dependencies.setdefault(node, set())
        self._dependents.setdefault(node, set())
        
        for name in self._dependency_names(recipe, kind):
            dependency = self._load_dependency(name, recipe, kind)
            dependency_node = DependencyNode(dependency.name, kind)

            self._dependencies[node].add(dependency_node)
            self._dependents.setdefault(dependency_node, set())
            self._dependents[dependency_node].add(node)
            
            self._resolve(dependency, kind)
        
        self._resolving.remove(node)
        self._resolved.add(node)
    
    @property
    def recipes(self) -> dict[DependencyNode, BuildRecipe]:
        """
        Returns all recipes contained in the resolved graph.
        """
        return dict(self._recipes)
    
    def dependencies_of(self, recipe: str | BuildRecipe, kind: DependencyKind) -> set[DependencyNode]:
        """
        Returns a list of all dependencies of a recipe.

        Args:
            recipe (str | BuildRecipe): The recipe to check.
            kind (DependencyKind): The kind of dependency to check.
        """

        name = recipe if isinstance(recipe, str) else recipe.name
        node = DependencyNode(name, kind)
        return set(self._dependencies[node])

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