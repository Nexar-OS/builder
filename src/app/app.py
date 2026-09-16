from argparse import ArgumentParser
from .command import *

def build_parser() -> ArgumentParser:
    # Create default parser
    parser = ArgumentParser(
        prog="builder",
        description="A build orchestration system."
    )
    DefaultArguments.populate_parser(parser)

    # Create subcommands
    subparsers = parser.add_subparsers(
        title="command",
        required=True
    )

    BuildCommand.add_to_parser(subparsers)
    CheckCommand.add_to_parser(subparsers)
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