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

class DependencyGraph():
    """
    Directed dependency graph for a collection of recipes.
    Resolves the dependency closure for a single dependency kind.
    """
    def __init__(self,
                 recipes: Iterable[BuildRecipe],
                 registry: "RecipeRegistry",
                 kind: DependencyKind,
                 allow_cycles: bool = False,
                 ignore_dependency_errors: bool = False
                ) -> None:
        self.registry = registry
        self.kind = kind
        self.allow_cycles = allow_cycles
        self.ignore_dependency_errors = ignore_dependency_errors

        self._recipes: dict[RecipeKey, BuildRecipe] = {}

        self._dependents: dict[RecipeKey, set[RecipeKey]] = {}
        self._dependencies: dict[RecipeKey, set[RecipeKey]] = {}

        self._resolved: set[RecipeKey] = set()
        self._resolving: set[RecipeKey] = set()

        for recipe in recipes:
            self._resolve(recipe)

    @classmethod
    def empty(cls) -> "DependencyGraph":
        """
        Return an empty and invalid dependency graph.
        """
        from .registry import RecipeRegistry
        return DependencyGraph(
            recipes=[],
            registry=RecipeRegistry([]),
            kind=DependencyKind.BUILD
        )

    def _load_dependency(self, key: RecipeKey, parent: BuildRecipe) -> BuildRecipe | None:
        """
        Resolve a dependency through the registry.

        Args:
            name (str): The name of the dependency to resolve.
            parent (BuildRecipe): The parent recipe that requires it.

        Returns:
            BuildRecipe: The loaded dependency.
        """

        dependency = self.registry.get(
            name=key.name,
            role=key.role,
            ctx=parent.ctx
        )

        if not dependency and not self.ignore_dependency_errors:
            raise RuntimeError(
                f"Recipe '{parent.name}' depends on '{key.name}', "
                f"but recipe '{key.name}' could not be loaded."
            )
        
        return dependency

    def _dependency_names(self, recipe: BuildRecipe) -> Iterable[RecipeKey]:
        """
        Return the dependencies relevant to this graph.
        """
        from .recipe import BuildRole
        
        match self.kind:
            case DependencyKind.BUILD:
                yield from (
                    RecipeKey(
                        name=dependency,
                        role=BuildRole.SYSROOT
                    )
                    for dependency in (recipe.dependencies.build or [])
                )
            
            case DependencyKind.RUNTIME:
                yield from (
                    RecipeKey(
                        name=dependency,
                        role=BuildRole.TARGET
                    )
                    for dependency in (recipe.dependencies.required or [])
                )
        
            case _:
                raise ValueError(f"Unhandled dependency kind: '{self.kind!r}'")

    def _resolve(self, recipe: BuildRecipe):
        """
        Recursively resolve a recipe and all of its dependencies.

        Args:
            recipe (BuildRecipe): The recipe to resolve.
            kind (DependencyKind): The kind of dependencies to resolve.
        """
        key = RecipeKey.get(recipe)

        if key in self._resolved:
            return
        
        if key in self._resolving:
            # Ignore cycles if allowed
            if self.allow_cycles:
                return
            
            raise DependencyCycleError(
                f"Dependency cycle involving '{recipe}'."
            )
        
        self._resolving.add(key)

        self._recipes[key] = recipe
        self._dependencies.setdefault(key, set())
        self._dependents.setdefault(key, set())
        
        for dependency_key in self._dependency_names(recipe):
            dependency = self._load_dependency(dependency_key, recipe)

            # Dependency errors are ignored
            # thus simply skip this dependency
            if not dependency:
                continue

            self._dependencies[key].add(dependency_key)
            self._dependents.setdefault(dependency_key, set())
            self._dependents[dependency_key].add(key)
            
            self._resolve(dependency)
        
        self._resolving.remove(key)
        self._resolved.add(key)
    
    @property
    def recipes(self) -> dict[RecipeKey, BuildRecipe]:
        """
        Returns all recipes contained in the resolved graph.
        """
        return dict(self._recipes)
    
    def dependencies_of(self, recipe: RecipeKey | BuildRecipe) -> set[RecipeKey]:
        """
        Returns a list of all dependencies of a recipe.

        Args:
            recipe (RecipeKey | BuildRecipe): The recipe to check.
        """

        key = recipe if isinstance(recipe, RecipeKey) else RecipeKey.get(recipe)

        return set(self._dependencies[key])

    def dependents_of(self, recipe: RecipeKey | BuildRecipe) -> set[RecipeKey]:
        """
        Returns a list of all dependents of a recipe.

        Args:
            recipe (RecipeKey | BuildRecipe): The recipe to check.
        """

        key = recipe if isinstance(recipe, RecipeKey) else RecipeKey.get(recipe)
        return set(self._dependents[key])


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