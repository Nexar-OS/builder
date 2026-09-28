from argparse import ArgumentParser, _SubParsersAction
from .command import *

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

    build_recipe_parser(subparsers)

    BuildCommand.add_to_parser(subparsers)
    PackageCommand.add_to_parser(subparsers)

    return parser

def build_recipe_parser(parent: _SubParsersAction):
    # builder recipe ...
    parser = parent.add_parser(
        name="recipe",
        help="Create, manage and modify package recipes directly from the cli."
    )

    subparsers = parser.add_subparsers(
        title="command",
        required=True
    )

    CheckCommand.add_to_parser(subparsers)

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