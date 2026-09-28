from typing import Literal, Any
import re
from builder.recipe.schema import *
from builder.build import BuildContext
from builder.recipe.recipe import GenericRecipe, BuildRole, BuildMethod
from builder.recipe.loader import load_recipe_from_schema, load_version_source_from_schema
from builder.utils.download import url_file_to_md5

class RecipeGenerator():
    """Generate new package recipes.

    ``RecipeGenerator`` provides convenient constructors for creating a
    :class:``RecipeSchema``.

    The generator operates entirely on the declarative recipe schema.
    """
    VERSION_PATTERN = r"(?P<version>[0-9][A-Za-z0-9._+-]*)"

    def __init__(self, schema: RecipeSchema) -> None:
        self.schema = schema

    @classmethod
    def empty(cls, name: str) -> "RecipeGenerator":
        """Create a minimal recipe for a package.

        Args:
            name (str): Name of the package.

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
    
    @classmethod
    def from_source(
        cls,
        name: str,
        version_source: VersionSourceSchema,
        download_url: str | None = None,
        homepage: str | None = None,
    ) -> "RecipeGenerator":
        """Construct a recipe generator from a specific type of ``VersionSource``.

        If ``download_url`` is passed, it will be added as a tarball source.

        Args:
            name (str): The name of the recipe.
            version_source (VersionSourceSchema): The version source to use.
            download_url (str | None, optional): An optional tarball source. Defaults to None.
            homepage (str | None, optional): Optional upstream homepage.
        """
        generator = RecipeGenerator.empty(name)
        generator.set("version_source", version_source)

        if download_url:
            generator.add_tarball(
                url=download_url,
                name=name,
            )
        
        if homepage:
            generator.schema.homepage = homepage

        return generator
    
    @classmethod
    def github(
        cls,
        repository: str,
        include_prereleases: bool = False,
        identifier: str = "releases",
        tag_format: str = "{version}",
        *,
        filename: str,
        name: str | None = None
    ) -> "RecipeGenerator":
        """Create a recipe from a Github repository.

        The repository should be specified using the convnetional
        ``owner/repository`` format.

        Args:
            repository (str): The repository.
            name (str | None, optional): Package name. Defaults to the repository name.
            include_prereleases (bool): Whether prerelease versions should be considered
                                        when discovering versions.
            tag_format (str): The format of gitlab-tags (Allows for ``{version}`` placeholder.)
            filename (str): The filename to download (Allows for ``{version}`` placeholder.)
            identifier (str): GitHub release identifier used by the version source.
        """
        if "/" not in repository:
            raise ValueError("Github repository must be in 'owner/repository' format!")
        
        repository_name = repository.rsplit("/", 1)[1]
        tag_format = tag_format.replace("{version}", "${version}")
        filename = filename.replace("{version}", "${version}")

        return cls.from_source(
            name=name or repository_name,
            version_source=GithubVersionSourceSchema(
                type="github",
                repo=repository,
                include_prereleases=include_prereleases,
                identifier=identifier
            ),
            download_url=f"https://github.com/{repository}/releases/download/{tag_format}/{filename}",
            homepage=f"https://github.com/{repository}/"
        )
        
    
    @classmethod
    def gitlab(
        cls,
        repository: str,
        include_prereleases: bool = False,
        tag_format: str = "{version}",
        *,
        filename: str,
        name: str | None = None,
        base_url: str | None = None,
    ) -> "RecipeGenerator":
        """Create a recipe from a Gitlab repository.

        The repository should be specified using the convnetional
        ``namespace/project`` format.

        Args:
            repository (str): The repository.
            name (str | None, optional): Package name. Defaults to the repository name.
            include_prereleases (bool): Whether prerelease versions should be considered
                                        when discovering versions.
            tag_format (str): The format of gitlab-tags (Allows for ``{version}`` placeholder.)
            filename (str): The filename to download (Allows for ``{version}`` placeholder.)
            base_url (str | None, optional): GitLab instance URL. ``None`` uses the default GitLab instance.
        """
        if "/" not in repository:
            raise ValueError("Gitlab repository must be in 'namespace/project' format!")
        
        repository_name = repository.rsplit("/", 1)[1]
        tag_format = tag_format.replace("{version}", "${version}")
        filename = filename.replace("{version}", "${version}")

        return cls.from_source(
            name=name or repository_name,
            version_source = GitlabVersionSourceSchema(
                type="gitlab",
                repo=repository,
                include_prereleases=include_prereleases,
                base_url=base_url
            ),
            download_url=f"https://gitlab.com/{repository}/-/archive/{tag_format}/{filename}",
            homepage=f"https://gitlab.com/{repository}/"
        )

    @classmethod
    def web(
        cls,
        url: str,
        filename: str,
        *,
        name: str
    ) -> "RecipeGenerator":
        """Create a recipe using a generic web version source.

        This constructor is useful when a project's upstream source
        is a web-archive.

        Returns:
            RecipeGenerator: A generator containing a web-based recipe source.
        """

        if filename.count("{version}") != 1:
            raise ValueError("source_format must contain exactly one '{version}' placeholder!")

        prefix, suffix = filename.split("{version}")
        version_regex = (
            f"{re.escape(prefix)}"
            f"{cls.VERSION_PATTERN}"
            f"{re.escape(suffix)}"
        )

        return cls.from_source(
            name=name,
            version_source=WebVersionSourceSchema(
                type="web",
                url=url,
                regex=version_regex
            ),
            download_url=(
                f"{url.rstrip('/')}/"
                f"{filename.replace('{version}', '${version}')}"
            ),
            homepage=url
        )

    def latest_version(self) -> "RecipeGenerator":
        """Set the version field to the latest upstream version.
        
        Uses the ``version_source`` of the schema to detect
        the latest upstream version.
        """
        source = load_version_source_from_schema(self.schema.version_source)
        if not source:
            return self
        
        latest = source.latest_version
        self.schema.version = latest.raw

        return self

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
                           md5hash: str | None = None,
                           strip_top_level: bool = True) -> "RecipeGenerator":
        """Add a tarball source to the recipe.

        Args:
            url (str): The url to the tarball (supports ${version} placeholder).
            name (str | None): The name of the source (defaults to ``self.schema.name``).
            filename (str | None): Name of the downloaded file.
            md5hash (str | None): md5hash of the file (defaults to "none" and will be resolved with ``._resolve_auto_hashes``)

        Returns:
            RecipeGenerator: This generator, allowing for method chaining.
        """
        if name is None:
            name = self.schema.name

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
    
    def autotools(
            self,
            install_target: str = "install",
            config_args: list[str] | None = None,
            build_args: list[str] | None = None,
            install_args: list[str] | None = None,
            build_method: BuildMethod | None = None,
            disable_fakeroot: bool = False,
            skip_build: bool = False,
        ) -> "RecipeGenerator":
        """Configure the autotools build system."""

        self.schema.build = BuildSchema(
            method=build_method or BuildMethod.OUT_OF_SOURCE,
            build_system=AutotoolsSchema(
                type="autotools",
                disable_fakeroot=disable_fakeroot,
                skip_build=skip_build,
                install_target=install_target,
                config_args=config_args,
                build_args=build_args,
                install_args=install_args
            )
        )

        return self
    
    def cmake(
            self,
            config_args: list[str] | None = None,
            build_args: list[str] | None = None,
            install_args: list[str] | None = None,
            build_method: BuildMethod | None = None,
            generator: str | None = None
        ) -> "RecipeGenerator":
        """Configure the cmake build system."""

        self.schema.build = BuildSchema(
            method=build_method or BuildMethod.OUT_OF_SOURCE,
            build_system=CMakeSchema(
                type="cmake",
                config_args=config_args,
                build_args=build_args,
                install_args=install_args,
                generator=generator
            )
        )

        return self
    
    def meson(
            self,
            config_args: list[str] | None = None,
            build_args: list[str] | None = None,
            install_args: list[str] | None = None,
            disable_fakeroot: bool = False,
            build_method: BuildMethod | None = None,
        ) -> "RecipeGenerator":
        """Configure the meson build system."""

        self.schema.build = BuildSchema(
            method=build_method or BuildMethod.OUT_OF_SOURCE,
            build_system=MesonSchema(
                type="meson",
                disable_fakeroot=disable_fakeroot,
                config_args=config_args,
                build_args=build_args,
                install_args=install_args
            )
        )

        return self
    
    def custom_build_system(
            self,
            prepare: str | None = None,
            configure: str | None = None,
            build: str | None = None,
            install: str | None = None,
            disable_fakeroot: bool = False,
            build_method: BuildMethod | None = None,
        ) -> "RecipeGenerator":
        """Configure the recipe to use a custom build system."""

        self.schema.build = BuildSchema(
            method=build_method or BuildMethod.OUT_OF_SOURCE,
            build_system=CustomBuildSystemSchema(
                type="custom",
                prepare=prepare,
                configure=configure,
                build=build,
                install=install,
                disable_fakeroot=disable_fakeroot,
            )
        )

        return self

    def add_patch(self, patch: Path) -> "RecipeGenerator":
        """Add a patch to the recipe.

        Args:
            patch (str): The relative path to the patch file.

        Returns:
            RecipeGenerator: This generator, allowing for method chaining.
        """
        if not self.schema.build:
            raise ValueError("Cannot add patch to a recipe without a build system.")

        patches: list[Path] = self.schema.build.patches or []
        patches.append(patch)

        self.schema.build.patches = list(set(patches))

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
    
    def _resolve_auto_hashes(self):
        """Calculate deferred source hashes after the source is known."""
        for source in self.schema.sources:
            if not any(isinstance(source, schema) for schema in [
                FileSourceSchema,
                TarballSourceSchema
            ]):
                continue

            if source.md5hash:
                continue

            if not self.schema.version:
                raise ValueError("Cannot resolve md5hashes automatically without a version.")

            source.md5hash = url_file_to_md5(source.url.replace("${version}", self.schema.version))
    
    def dump(self) -> dict[str, Any]:
        """Create a dump of the recipe schema to serialize.

        Returns:
            dict[str, Any]: Mapping of all values.
        """
        return self.schema.model_dump(
            exclude_none=True,
            mode="json",
            exclude_defaults=True,
        )