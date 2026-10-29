import os
import subprocess

from pathlib import Path
from typing import Mapping, Any, TYPE_CHECKING

from .context import BuildContext
from .environment import (
    Environment,
    EnvironmentProfile
)

if TYPE_CHECKING:
    from builder.recipe import BuildRecipe

class CommandRunner:
    """
    Execute commands with an explicit build environment.

    The reunner provides a single invocation interface for build systems.
    """

    def __init__(
            self,
            ctx: BuildContext,
            *,
            default_profile: EnvironmentProfile = EnvironmentProfile.TARGET
        ) -> None:
        self.ctx = ctx
        self.default_profile = default_profile
    
    def make_environment(self,
                         *,
                         profile: EnvironmentProfile | None = None,
                         environment: Environment | Mapping[str, str] | None = None,
                         overrides: Mapping[str, str] | None = None,
                         unset: tuple[str, ...] = ()
                        ) -> dict[str, str]:
        """Construct the environment dictionary for a command.

        Args:
            profile (EnvironmentProfile | None, optional): Profile to construct when ``environment`` is omitted.
            environment (Environment | Mapping[str, str]): An already constructed ``Environment`` or a mapping of environment variables.
            overrides (Mapping[str, str] | None, optional): Variables to add or replace for this invocation. Defaults to None.
            unset (tuple[str, ...], optional): Variables to remove from the enviroment. Defaults to ().

        Returns:
            dict[str, str]: A mutable dictionary suitable for ``subprocess.run``.
        """

        # No environment was passed
        if environment is None:
            selected_profile = profile or self.default_profile
            selected_environment = Environment.from_context(
                ctx=self.ctx,
                profile=selected_profile
            )
            variables = selected_environment.as_dict()
        
        # Environment passed was an Environment object
        elif isinstance(environment, Environment):
            variables = environment.as_dict()
        
        # Environment passed was already a dict
        else:
            variables = dict(environment)
        
        for key in unset:
            variables.pop(key, None)
        
        if overrides:
            variables.update(overrides)
        
        return variables
    
    def run(
            self,
            cmd: list[str],
            *,
            profile: EnvironmentProfile | None = None,
            environment: Environment | None = None,
            env_overrides: Mapping[str, str] | None = None,
            unset_env: tuple[str, ...] = (),
            check: bool = True,
            use_fakeroot: bool = True,
            recipe: "BuildRecipe | None" = None,
            cwd: str | Path | None = None,
            **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        """Execute a command and return its completed-process result.

        Args:
            cmd (list[str]): Command and arguments to execute.
            profile (EnvironmentProfile | None, optional): Environment profile for this invocation. Ignored if ``environment`` is passed.
            environment (Environment | None, optional): Optional preconstructed environment.
            env_overrides (Mapping[str, str] | None, optional): Environment variables to add or override.
            unset_env (tuple[str, ...], optional): Environment variables to remove.
            check (bool, optional): Raises RuntimeError if the command exits unsuccessfully.
            use_fakeroot (bool, optional): Prefix the command with ``fakeroot`` when enabled.
            recipe (BuildRecipe | None, optional): Optional recipe whose logger and information will be made available in the environment.
            cwd (str | Path | None, optional): Optional working directory for the subprocess.
            **kwargs: Additional keyword arguments passed to ``subprocess.run``.
        """

        if not cmd:
            raise ValueError("Cannot execute empty command.")
        
        command = [
            os.fspath(argument)
            for argument in cmd
        ]

        # Get logger
        if recipe is not None:
            logger = recipe.logger
        else:
            from builder.utils.logger import global_logger
            logger = global_logger

        # Prefix command with fakeroot if enabeld
        if use_fakeroot:
            command.insert(0, "fakeroot")
        
        env = self.make_environment(
            profile=profile,
            environment=environment,
            overrides=env_overrides,
            unset=unset_env,
        )

        logger.debug(f"> {' '.join(command)}")

        # Keep output available for reporting errors.
        kwargs.setdefault("capture_output", True)
        kwargs.setdefault("text", True)

        result = subprocess.run(
            command,
            env=env,
            cwd=Path(cwd) if cwd is not None else None,
            **kwargs
        )

        # Check for errors
        if check and result.returncode != 0:
            stdout = result.stdout or ""
            stderr = result.stderr or ""

            logger.error(
                f"Command failed with exit code {result.returncode}: "
                f"{' '.join(command)}\n\n"
                f"STDOUT:\n{stdout}\n\n"
                f"STDERR:\n{stderr}\n\n"
            )

            raise RuntimeError(
                f"Command failed with exit code {result.returncode}: "
                f"{' '.join(command)}\n"
                f"{stderr}"
            )

        return result