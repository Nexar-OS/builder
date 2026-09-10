from dataclasses import dataclass

from builder.stage import Stage

from uuid import uuid4
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
        
        stage = Stage(
            ctx=ctx,
            name=self.export or str(uuid4()),
            recipes=recipes,
            build_role=BuildRole.TARGET,
            add_runtime_dependencies=not self.no_runtime_dependencies,
            ignore_dependency_errors=self.ignore_dependency_errors,
        )

        stage.build()

        if self.export:
            stage.export(copy=True)