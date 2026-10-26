from dataclasses import dataclass

from builder.stage import Stage

from uuid import uuid4
from builder.utils.logger import error
from builder.build import BuildContext
from builder.recipe import BuildRole
from .command import CLICommand, CLIArgument

@dataclass
class BuildCommand(CLICommand):
    name = "build"

    recipes: list[str] = CLIArgument(
        type=str,
        help="Pass one or multiple recipe(s) to build.",
        positional=True
    ).arg(parse=list[str])

    use_all: bool = CLIArgument(
        type=bool,
        help="Select all available recipes over all repositories passed to the registry.",
        flags=("--all", "-a")
    ).arg()

    verbose: bool = CLIArgument(
        type=bool,
        help="Make recipe builds verbose.",
        flags=("--verbose", "-v")
    ).arg()

    skip: list[str] = CLIArgument(
        type=str,
        help="Pass one or multiple recipe(s) to exclude from the '--all' selection.",
        flags=("--skip", "-s")
    ).arg(parse=list[str])

    throw_on_fail: bool = CLIArgument(
        type=bool,
        help="Pass to exit the builder when a single recipe cannot be built.",
        flags=("--throw-on-fail", "-tof"),
    ).arg()

    max_retries: int = CLIArgument(
        type=int,
        help="The maximum amount to retry building each recipe if it fails.",
        flags=("--max-retries", "-r"),
        default=3
    ).arg()

    no_runtime_dependencies: bool = CLIArgument(
        type=bool,
        help="If passed, runtime dependencies won't be added to recipe list.",
        flags=("--no-runtime-deps", "-nrd")
    ).arg()

    ignore_dependency_errors: bool = CLIArgument(
        type=bool,
        help="If passed, dependency errors (such as cycles) will be ignored.",
        flags=("--ignore-dependency-errors", "-ide")
    ).arg()

    role: str = CLIArgument(
        type=str,
        help="Set the role to build the recipe as.",
        flags=("--role", "-rl"),
        metavar="/".join( x.name for x in list(BuildRole) )
    ).arg()

    export: str = CLIArgument(
        type=str,
        help="Export the recipes after building into a stage.",
        flags=("--export", "-e")
    ).arg()

    def handle(self, ctx: BuildContext):
        if self.use_all:
            recipes: list[str] = list(ctx.registry.all)
        else:
            recipes: list[str] = self.recipes
        
        if self.skip:
            recipes = [ recipe for recipe in recipes if not recipe in self.skip ]

        if not recipes:
            error("Please pass one or more recipes to build.")
            return
    
        if self.verbose:
            ctx.verbose_build_logs = True

        role: BuildRole = BuildRole.TARGET
        if self.role:
            for b in list(BuildRole):
                if b.name.lower() == self.role.lower():
                    role = b
                    break
            
            error(f"Invalid build role '{self.role}'")

        stage = Stage(
            ctx=ctx,
            name=self.export or str(uuid4()),
            recipes=recipes,
            build_role=role,
            add_runtime_dependencies=(
                (not self.no_runtime_dependencies) if role == BuildRole.TARGET
                else False
            ),
            ignore_dependency_errors=self.ignore_dependency_errors,
            max_retries=self.max_retries,
            throw_on_fail=self.throw_on_fail,
        )

        stage.build()

        if self.export:
            stage.export(copy=True)