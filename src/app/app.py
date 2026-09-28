from argparse import ArgumentParser, _SubParsersAction
from .command import *

def _create_group(name: str, description: str, parent: _SubParsersAction, commands: list[type[CLICommand]]):
    parser = parent.add_parser(
        name=name,
        help=description
    )

    subparsers = parser.add_subparsers(
        title="command",
        required=True
    )

    for command in commands:
        command.add_to_parser(subparsers)

def build_parser() -> ArgumentParser:
    # Create default parser
    parser = ArgumentParser(
        prog="builder",
        description="The official nexar package build (orchestration) system."
    )
    DefaultArguments.populate_parser(parser)

    # Create subcommands
    subparsers = parser.add_subparsers(
        title="command",
        required=True
    )

    _create_group(
        name="recipe",
        description="Create, manage and modify package recipes directly from the cli.",
        parent=subparsers,
        commands=[
            CheckCommand,
            CreateRecipeCommand
        ]
    )

    BuildCommand.add_to_parser(subparsers)
    PackageCommand.add_to_parser(subparsers)

    return parser

def cli():
    # Load parser
    parser = build_parser()
    args = parser.parse_args()

    # Load default arguments
    default_args = DefaultArguments.from_namespace(args)
    default_args.prepare_environment()

    # Invoke subcommand
    commandClass: CLICommand = args.command_class.from_namespace(args)
    commandClass.handle(default_args.ctx)