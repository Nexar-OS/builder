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

    version: str = CLIArgument(
        type=str,
        help="The upstream-version to build the package from.",
        flags=("--version", "-v"),
        default=""
    ).arg()

    def handle(self, ctx: BuildContext):
        gen = RecipeGenerator.empty(name=self.recipe_name) \
            .set("homepage", self.homepage) \
            .set("license", self.licenses) \
            .set("description", self.description) \
            .set("version", self.version) \
            .set("maintainers", self.maintainers) \
            .set("dependencies", Dependencies(
                required=self.runtime_dependencies,
                optional=self.optional_runtime_dependencies,
                build=self.build_dependencies
            )) \

        print(gen.schema)