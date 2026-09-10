from pathlib import Path
from argparse import ArgumentParser

from app.command import *

from builder.build import *
from builder.recipe import *

parser = ArgumentParser(
    prog="builder",
    description="A build orchestration system."
)

DefaultArguments.populate_parser(parser)

subparsers = parser.add_subparsers(
    title="command",
    required=True
)

BuildCommand.add_to_parser(subparsers)

args = parser.parse_args()

default_args = DefaultArguments.from_namespace(args)


commandClass: CLICommand = args.command_class.from_namespace(args)
commandClass.handle(default_args.ctx)