from typing import TypeVar
from pathlib import Path
from builder.recipe.schema import *
from builder.recipe import GenericRecipe, BuildRole
from builder.utils.data import load_yaml
from builder.utils.logger import warn
from builder.source import *
from builder.build.system import *

def load_schema(path: Path) -> RecipeSchema | None:
    """
    Loads a recipe schema from a file.

    Args:
        path (Path): The path to the schema file.

    Returns:
        RecipeSchema | None: The loaded schema or None if the file wasn't found or the schema was invalid.
    """

    yaml = load_yaml(path)

    if not yaml:
        return None

    try:
        return RecipeSchema.model_validate(yaml)
    except:
        warn(f"Failed to parse schema for '{path}'")
        return None


SchemaT = TypeVar("SchemaT", bound=Schema)
ResultT = TypeVar("ResultT")

def _load_class_from_schema(schema: SchemaT, types: dict[type[SchemaT], type[ResultT]]) -> ResultT:
    """
    Create a domain object from a ``Schema``.

    The schema's concrete type is used to select the corresponding domain
    class from ``types``. The schema's ``type`` field is dropped before passing
    it to the constructor.

    Args:
        schema (Schema): The schema to convert.
        types (dict[type, type]): A mapping from schema types to their corresponding domain classes.

    Returns:
        An instance of the domain class.
    """
    source_class = types[type(schema)]
    dump = schema.model_dump()
    dump.pop("type")
    return source_class(**dump)

def load_source_from_schema(schema: SourceSchema) -> Source:
    """
    Loads a source from its schema.

    Args:
        schema (SourceSchema): The schema to load
    """

    return _load_class_from_schema(schema, {
        TarballSourceSchema: TarballSource,
        FileSourceSchema: FileSource
    })

def load_build_system_from_schema(schema: BuildSystemSchema) -> BuildSystem:
    return _load_class_from_schema(schema, {
        AutotoolsSchema: Autotools,
        CMakeSchema: CMake,
        MesonSchema: Meson
    })

def load_recipe_from_schema(role: BuildRole, schema: RecipeSchema) -> GenericRecipe:
    """
    Loads a ``GenericRecipe`` out of a ``RecipeSchema``

    Args:
        role (BuildRole): The role the recipe should be built in.
        schema (RecipeSchema): The schema to load.

    Returns:
        GenericRecipe: The loaded recipe
    """
    return GenericRecipe(
        role=role,
        name=schema.name,
        version=schema.version,
        sources=[ load_source_from_schema(source_schema)
                  for source_schema in schema.sources ],
        dependencies=schema.dependencies,
        build_method=schema.build.method,
        build_system=load_build_system_from_schema(schema.build.build_system),
        patches=schema.build.patches,
        prepare_script=schema.build.prepare,
        post_install_script=schema.build.post_install
    )

def load_recipe(recipe_path: Path, role: BuildRole) -> GenericRecipe | None:
    """
    Loads and parses a recipe from a schema file.

    Args:
        recipe_path (Path): The path to the recipe file.

    Returns:
        GenericRecipe | None: The loaded recipe or None if schema was invalid.
    """
    schema = load_schema(recipe_path)

    if not schema:
        return None

    return load_recipe_from_schema(role, schema)