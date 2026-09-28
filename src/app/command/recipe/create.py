from pathlib import Path
from dataclasses import dataclass

from builder.build.context import BuildContext
from builder.utils.logger import error
from ..command import CLICommand, CLIArgument

from builder.recipe import RecipeGenerator, Dependencies

@dataclass
class CreateRecipeCommand(CLICommand):
    name = "create"

    recipe_name: str = CLIArgument(
        type=str,
        help="The name of the recipe to create.",
    ).arg()

    description: str = CLIArgument(
        type=str,
        help="A human-readable description of the package.",
        flags=("--desc", "-d"),
        default=""
    ).arg()

    homepage: str = CLIArgument(
        type=str,
        help="The representative homepage of the upstream project.",
        flags=("--homepage", "-hp"),
        default=""
    ).arg()

    licenses: list[str] = CLIArgument(
        type=str,
        help="The license of the package. (Can be passed multiple times.)",
        flags=("--license", "-l"),
        action="append",
        default=[]
    ).arg(parse=list[str])

    maintainers: list[str] = CLIArgument(
        type=str,
        help="The maintainer(s) of this packages recipe (May be passed multiple times).",
        flags=("--maintainer", "-m"),
        action="append",
        default=[]
    ).arg(parse=list[str])

    runtime_dependencies: list[str] = CLIArgument(
        type=str,
        help="Add a runtime dependency.",
        flags=("--runtime-dep", "-rd"),
        action="append",
        default=[]
    ).arg(parse=list[str])

    optional_runtime_dependencies: list[str] = CLIArgument(
        type=str,
        help="Add an optional runtime dependency.",
        flags=("--opt-runtime-dep", "-ord"),
        action="append",
        default=[]
    ).arg(parse=list[str])

    build_dependencies: list[str] = CLIArgument(
        type=str,
        help="Add a dependency required for building this recipe.",
        flags=("--build-dep", "-bd"),
        action="append",
        default=[]
    ).arg(parse=list[str])

    version: str | None = CLIArgument(
        type=str,
        help="The upstream-version to build the package from.",
        flags=("--version", "-v")
    ).arg()

    template: str | None = CLIArgument(
        type=str,
        help="Select an optional recipe template",
        flags=("--template", "-t"),
        metavar="[template]"
    ).arg()

    url: str | None = CLIArgument(
        type=str,
        help="URL pointing to a public web-archive.",
        flags=("--url", "-u"),
        metavar="[name-{version}.tar.xz]"
    ).arg()

    repo: str | None = CLIArgument(
        type=str,
        help="The repository to use with --template=github|gitlab",
        flags=("--repo", "-r"),
        metavar="owner/repo"
    ).arg()

    include_prereleases: bool = CLIArgument(
        type=bool,
        help="When passed, prereleases will be considered with version discovery.",
        flags=("--include-prereleases", "-ipr")
    ).arg()

    release_identifier: str = CLIArgument(
        type=str,
        help="The github release identifier. (Usually either tags or releases)",
        flags=("--release-identifier", "-ri"),
        default="releases"
    ).arg()

    tag_format: str = CLIArgument(
        type=str,
        help="The format of gitlab-tags (Allows for ``{version}`` placeholder.)",
        flags=("--tag-format", "-tf"),
        default="{version}",
        metavar="[{version}, v{version}, version-{version}, etc.]"
    ).arg()

    gitlab_url: str | None = CLIArgument(
        type=str,
        help="The url of the gitlab instance.",
        flags=("--gitlab", "-gl"),
        metavar="https://gitlab.com"
    ).arg()

    filename: str | None = CLIArgument(
        type=str,
        help="The source filename to search for.",
        flags=("--filename", "-fn"),
        metavar="[name-{version}.tar.xz]"
    ).arg()

    in_source: bool = CLIArgument(
        type=bool,
        help="Set the build method to IN_SOURCE.",
        flags=("--in-source", "-is")
    ).arg()

    patches: list[Path] = CLIArgument(
        type=Path,
        help="Add a patch to the recipe.",
        flags=("--add-patch", "-p"),
        action="append",
        default=[]
    ).arg()

    def _generator(self) -> RecipeGenerator | None:        
        generator = None

        match (self.template or "default").lower():
            case "default":
                generator = RecipeGenerator.empty(name=self.recipe_name)

            case "web":
                if not self.url:
                    error(f"'Web' template needs '--url' to run.")
                    return
                
                if not self.filename:
                    error(f"'Web' template needs '--filename' to run.")
                    return

                generator = RecipeGenerator.web(
                    url=self.url,
                    filename=self.filename,
                    name=self.recipe_name
                )
            
            case "github":
                if not self.repo:
                    error(f"'Github' template needs '--repo' to run.")
                    return
                
                if not self.filename:
                    error(f"'Github' template needs '--filename' to run.")
                    return

                generator = RecipeGenerator.github(
                    repository=self.repo,
                    include_prereleases=self.include_prereleases,
                    identifier=self.release_identifier,
                    tag_format=self.tag_format,
                    filename=self.filename,
                    name=self.recipe_name
                )
            
            case "gitlab":
                if not self.repo:
                    error(f"'Github' template needs '--repo' to run.")
                    return
                
                if not self.filename:
                    error(f"'Github' template needs '--filename' to run.")
                    return

                generator = RecipeGenerator.gitlab(
                    repository=self.repo,
                    include_prereleases=self.include_prereleases,
                    tag_format=self.tag_format,
                    filename=self.filename,
                    name=self.recipe_name,
                    base_url=self.gitlab_url
                )
            
            case _:
                error(f"Unrecognized template '{self.template}'!")

        if generator:
            return self._complete_generator(generator)

    def _complete_generator(self, generator: RecipeGenerator) -> RecipeGenerator:
        generator \
            .set("license", self.licenses)        \
            .set("description", self.description) \
            .set("maintainers", self.maintainers) \
            .set("homepage", self.homepage or generator.schema.homepage) \
            .set("dependencies", Dependencies(
                required=self.runtime_dependencies,
                optional=self.optional_runtime_dependencies,
                build=self.build_dependencies
            )) \

        for patch in self.patches:
            generator.add_patch(patch)
        
        # Either use the version passed
        # or try to find the latest upstream version
        if self.version:
            generator.set("version", self.version)
        else:
            generator.latest_version()

        generator._resolve_auto_hashes()
        
        return generator

    def handle(self, ctx: BuildContext):
        generator = self._generator()
        if not generator:
            return

        print(generator.schema)