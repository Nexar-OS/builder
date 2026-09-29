from pathlib import Path
from dataclasses import dataclass

from builder.build.context import BuildContext
from builder.utils.logger import error
from ..command import CLICommand, CLIArgument
from builder.recipe import RecipeGenerator, Dependencies, BuildMethod
import sys

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

    build_system: str | None = CLIArgument(
        type=str,
        help="The build system to use.",
        flags=("--build-system", "-bs"),
    ).arg()

    config_args: list[str] = CLIArgument(
        type=str,
        help="Add one or more configuration args to the build system.",
        flags=("--config-arg", "-c"),
        action="append",
        default=[]
    ).arg()

    build_args: list[str] = CLIArgument(
        type=str,
        help="Add one or more build args to the build system.",
        flags=("--build-arg", "-b"),
        action="append",
        default=[]
    ).arg()

    install_args: list[str] = CLIArgument(
        type=str,
        help="Add one or more install args to the build system.",
        flags=("--install-arg", "-i"),
        action="append",
        default=[]
    ).arg()

    disable_fakeroot: bool = CLIArgument(
        type=bool,
        help="Force the builder to break out of fakeroot when building the package.",
        flags=("--disable-fakeroot", "-dfr")
    ).arg()

    install_target: str = CLIArgument(
        type=str,
        help="Override the make install command.",
        flags=("--install-target",),
        metavar="make <install>",
        default="install"
    ).arg()

    generator: str = CLIArgument(
        type=str,
        help="Override the cmake generator.",
        flags=("--generator",)
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

    prepare: list[str] = CLIArgument(
        type=str,
        help="Add one or more lines of shell script to execute before the recipe gets build.",
        flags=("--prepare", "-prep"),
        action="append",
        default=[]
    ).arg()

    post_install: list[str] = CLIArgument(
        type=str,
        help="Add one or more lines of shell script to execute after the recipe has been built.",
        flags=("--post-install", "-pi"),
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

    def _parse_build_system(self, generator: RecipeGenerator) -> None:
        method = BuildMethod.IN_SOURCE if self.in_source else BuildMethod.OUT_OF_SOURCE
        match (self.build_system or "none").lower():
            case "meson":
                generator.meson(
                    config_args=self.config_args or None,
                    build_args=self.build_args or None,
                    install_args=self.install_args or None,
                    disable_fakeroot=self.disable_fakeroot,
                    build_method=method
                )
            
            case "autotools":
                generator.autotools(
                    install_target=self.install_target,
                    config_args=self.config_args or None,
                    build_args=self.build_args or None,
                    install_args=self.install_args or None,
                    build_method=method,
                    disable_fakeroot=self.disable_fakeroot
                )
            
            case "cmake":
                generator.cmake(
                    config_args=self.config_args or None,
                    build_args=self.build_args or None,
                    install_args=self.install_args or None,
                    build_method=method,
                    generator=self.generator
                )
            
            case "custom":
                generator.custom_build_system(
                    prepare=None,
                    configure="\n".join(self.config_args) or None,
                    build="\n".join(self.build_args) or None,
                    install="\n".join(self.install_args) or None,
                    disable_fakeroot=self.disable_fakeroot,
                    build_method=method
                )
            
            case "none":
                ...
            
            case _:
                raise ValueError(f"Unknown build system '{self.build_system}'!")

    def _complete_generator(self, generator: RecipeGenerator) -> RecipeGenerator:
        generator \
            .set("license", self.licenses or "unknown")        \
            .set("description", self.description or "empty") \
            .set("maintainers", self.maintainers or None) \
            .set("homepage", self.homepage or generator.schema.homepage or "unknown") \

        dependencies = Dependencies(
            required=self.runtime_dependencies or None,
            optional=self.optional_runtime_dependencies or None,
            build=self.build_dependencies or None
        )
        if not dependencies.is_empty():
            generator.set("dependencies", dependencies)
        

        # Set build system
        self._parse_build_system(generator)

        # Add hooks
        if self.post_install:
            generator.post_install(*self.post_install)
        
        if self.prepare:
            generator.prepare(*self.prepare)

        # Add patches
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
        
        sys.stdout.write(generator.yaml())