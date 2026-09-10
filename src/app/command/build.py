from argparse import ArgumentParser

from .command import CLICommand, CLIArgument

from dataclasses import dataclass, field

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

    def handle(self):
        print("Recipes: " + ", ".join(self.recipes))