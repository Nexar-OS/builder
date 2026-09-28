from typing import Literal, Any
from builder.recipe.schema import *
from builder.build.context import BuildContext
from builder.recipe.recipe import GenericRecipe, BuildRole
from builder.recipe.loader import load_recipe_from_schema
from builder.utils.download import url_file_to_md5

class RecipeGenerator():
    """Generate new package recipes.

    ``RecipeGenerator`` provides convenient constructors for creating a
    :class:``RecipeSchema``.

    The generator operates entirely on the declarative recipe schema.
    """
    def __init__(self, schema: RecipeSchema) -> None:
        self.schema = schema

    @classmethod
    def empty(cls, name: str) -> "RecipeGenerator":
        """Create a minimal recipe for a package.

        Args:
            name (str): Name of the package.
            homepage (str): Optional homepage value (Defaults to "").
            license (str): Optional license (Defaults to "").
            description (str): Optional human-readable package description (Defaults to "").
            version (str): Optional default-version (Defaults to "").

        Returns:
            RecipeGenerator: A generator containing a minimal recipe.
        """
        return cls(
            schema=RecipeSchema(
                name=name,
                homepage="",
                license="",
                description="",
                version=""
            )
        )
    
    def add_source(self, source: SourceSchema) -> "RecipeGenerator":
        """Add a source to the recipe.

        Args:
            source (SourceSchema): The source schema to add.

        Returns:
            RecipeGenerator: This generator, allowing for method chaining.
        """
        self.schema.sources.append(source)
        return self
    

    def add_tarball(self, 
                           url: str,
                           *,
                           name: str | None = None,
                           filename: str | None = None,
                           md5hash: str | Literal["auto"] | None = None,
                           strip_top_level: bool = True) -> "RecipeGenerator":
        """Add a tarball source to the recipe.

        Args:
            source (SourceSchema): The source schema to add.

        Returns:
            RecipeGenerator: This generator, allowing for method chaining.
        """
        if name is None:
            name = self.schema.name

        if md5hash == "auto":
            md5hash = url_file_to_md5(url)

        return self.add_source(
            TarballSourceSchema(
                type="tarball",
                name=name,
                url=url,
                filename=filename,
                md5hash=md5hash,
                strip_top_level=strip_top_level
            )
        )

    def set(self,
            field: Literal["name", "homepage", "license", "description", "version", "version_source", "maintainers", "dependencies", "sources", "build"],
            value: Any) -> "RecipeGenerator":
        """Set a field of this recipe.

        Args:
            field (str): The fields name.
            value (Any): The desired value

        Returns:
            RecipeGenerator: This generator, allowing for method chaining.
        """
        data = self.schema.model_dump()
        data[field] = value
        self.schema = RecipeSchema.model_validate(data)
        return self

    def set_build(self, build: BuildSchema) -> "RecipeGenerator":
        """Set the build configuration for the recipe.

        Args:
            build (BuildSchema): Build config.

        Returns:
            RecipeGenerator: This generator, allowing for method chaining.
        """
        self.schema.build = build
        return self
    
    def recipe(self, ctx: BuildContext, role: BuildRole | None = None) -> GenericRecipe:
        """Generate the runtime recipe from the declarative representation.

        Args:
            ctx (BuildContext): The build context for the recipe.
            role (BuildRole | None): The role for the recipe. (Defaults to BuildRole.TARGET).

        Returns:
            GenericRecipe: The recipe.
        """
        return load_recipe_from_schema(
            ctx=ctx,
            role=role or BuildRole.TARGET,
            schema=self.schema
        )