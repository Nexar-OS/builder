from pathlib import Path
from argparse import ArgumentParser

from app.command import *

from builder.build import *
from builder.recipe import *




# ctx = BuildContext(
#     registry                = RecipeRegistry([
#                                     Path(__file__).parent.parent / "recipe",
#                                     Path(__file__).parent.parent / "bundle",
#                                 ]),
#     build_dir               = Path("build").resolve(),
#     staging_dir             = Path("build/staging").resolve(),
#     metadata_dir            = Path("build/.metadata").resolve(),
#     build_machine           = detect_machine(),
#     target_machine          = Target.X86_64,
#     toolchain               = NativeToolchain(),
#     toolchain_dir           = Path("build/toolchain/binaries").resolve(),
#     toolchain_sysroot       = Path("build/toolchain/sysroot").resolve(),
#     num_jobs                = num_jobs,
#     verbose_build_logs      = False,
# )


def create_default_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="builder",
        description="A build orchestration system."
    )
    
    # Global options
    parser.add_argument(
        "--registry",
        "-r",
        action="append",
        type=Path,
        help="Add a directory of recipes to the recipe registries discovery.",
        default=[]
    )

    parser.add_argument(
        "--build",
        "-b",
        type=Path,
        help="Set the build directory.",
        default=Path("build")
    )

    parser.add_argument(
        "--staging",
        "-s",
        type=Path,
        help="Set the directory to export stages in to.",
        default=Path("build/staging")
    )

    parser.add_argument(
        "--toolchain",
        "-t",
        type=Path,
        help="Set the directory to store toolchains in.",
        default=Path("build/toolchain")
    )

    return parser

parser = create_default_parser()

subparsers = parser.add_subparsers(
    title="command",
    required=True
)

BuildCommand.add_to_parser(subparsers)

args = parser.parse_args()

commandClass: CLICommand = args.command_class.from_namespace(args)
commandClass.handle()