from argparse import ArgumentParser
from .command import *
from builder.stage import Stage
from builder.utils.logger import create_default_logger

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

    return parser

def cli():
    # Load parser
    parser = build_parser()
    args = parser.parse_args()

    # Load default arguments
    default_args = DefaultArguments.from_namespace(args)
    
    default_args.build_dir.mkdir(exist_ok=True, parents=True)

    Stage.DEFAULT_MAX_WORKERS = default_args.max_workers

    create_default_logger(default_args.build_dir / "build.log")

    # Invoke subcommand
    commandClass: CLICommand = args.command_class.from_namespace(args)
    commandClass.handle(default_args.ctx)