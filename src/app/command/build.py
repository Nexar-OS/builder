from dataclasses import dataclass

from builder.build import BuildContext
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

    def handle(self, ctx: BuildContext):
        if self.use_all:
            recipes: list[str] = list(ctx.registry.all)
        else:
            recipes: list[str] = self.recipes
        
        print(recipes)