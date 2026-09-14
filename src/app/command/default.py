from pathlib import Path
from dataclasses import dataclass

from builder.toolchain import *
from builder.build import *
from builder.recipe import *
from builder.stage import Stage
from builder.utils.logger import create_default_logger
from .command import CLICommand, CLIArgument


@dataclass
class DefaultArguments(CLICommand):
    registry: list[Path] = CLIArgument(
        type=Path,
        help="Add a directory of recipes to the recipe registries discovery.",
        action="append",
        flags=("--registry", "-r"),
        default=[]
    ).arg()

    build_dir: Path = CLIArgument(
        type=Path,
        help="Set the build directory.",
        flags=("--build", "-b"),
        default=Path("build/")
    ).arg()
    
    staging_dir: Path = CLIArgument(
        type=Path,
        help="Set the directory to export stages in to.",
        flags=("--staging", "-s"),
        default=Path("build/staging")
    ).arg()

    toolchain_dir: Path = CLIArgument(
        type=Path,
        help="Set the directory to store toolchains in.",
        flags=("--toolchain", "-t"),
        default=Path("build/toolchain")
    ).arg()
    
    max_workers: int = CLIArgument(
        type=int,
        help="Set the maximum amount of recipes that can be built concurrently. (Default is 'auto').",
        flags=("--max-workers", "-w"),
        default=detect_parallelism()[0]
    ).arg()

    num_jobs: int = CLIArgument(
        type=int,
        help="The maximum amount of make jobs. (Default is 'auto').",
        flags=("--num_jobs", "-j"),
        default=detect_parallelism()[1]
    ).arg()

    target: Literal["x86_64", "aarch64", "armv7"] = CLIArgument(
        type=str,
        help="The target machine to compile recipes for.",
        flags=("--target", "-tgt"),
        default=detect_machine().arch
    ).arg()

    def __post_init__(self) -> None:
        self._ctx = None

    def prepare_environment(self) -> None:
        """
        Prepare a proper build environment.
        """

        # Ensure build dir exists
        self.build_dir.mkdir(exist_ok=True, parents=True)

        # Create logger
        create_default_logger(self.build_dir / "build.log")

        # Set max workers
        Stage.DEFAULT_MAX_WORKERS = self.max_workers

    @property
    def ctx(self) -> BuildContext:
        """
        Constructs a BuildContext from command arguments.

        Returns:
            BuildContext: The passed context.
        """
        if not self._ctx:
            target = getattr(Target, self.target.upper(), None)
            if not target:
                raise RuntimeError(f"Invalid target '{self.target}'")

            self._ctx = BuildContext(
                registry=RecipeRegistry([
                    Path(__file__).parent.parent.parent / "recipe",
                    Path(__file__).parent.parent.parent / "bundle",
                    *self.registry,
                ]),
                build_dir=self.build_dir,
                staging_dir=self.staging_dir,
                metadata_dir=self.build_dir / ".metadata",
                build_machine=detect_machine(),
                target_machine=target,
                toolchain=NativeToolchain(),
                toolchain_dir=self.toolchain_dir / "binaries",
                toolchain_sysroot=self.toolchain_dir / "sysroot",
                num_jobs=self.num_jobs
            )
        
        return self._ctx