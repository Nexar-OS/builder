from pathlib import Path
from builder.recipe.schema import *
from builder.recipe import GenericRecipe, BuildRole
from builder.utils.data import load_yaml
from builder.source import *

def load_schema(path: Path) -> RecipeSchema:
    yaml = load_yaml(path)
    return RecipeSchema.model_validate(yaml)

def load_source_from_schema(schema: SourceSchema) -> Source:
    """
    Loads a source from its schema.

    Args:
        schema (SourceSchema): The schema to load

    Returns:
        _type_: The loaded source class.
    """
    
    SOURCE_TYPES = {
        TarballSourceSchema: TarballSource,
        FileSourceSchema: FileSource
    }

    source_class = SOURCE_TYPES[type(schema)]
    dump = schema.model_dump()
    dump.pop("type")
    return source_class(**dump)

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
        build_system=None
    )