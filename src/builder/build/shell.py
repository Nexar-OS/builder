import subprocess
import tempfile
import shlex
import os
import select

from pathlib import Path
from typing import Any, TYPE_CHECKING

from .environment import Environment

if TYPE_CHECKING:
    from builder.recipe import BuildRecipe

class Shell:
    """
    Execute commands with an explicit build environment.

    The runner provides a single invocation interface for build systems.
    """

    def __init__(
            self,
            environment: Environment,
            *,
            persistent: bool = True,
            recipe: "BuildRecipe | None" = None,
            **kwargs,
        ) -> None:
        self.persistent = persistent
        self._shell_cache: subprocess.Popen[str] | None = None
        self.environment: Environment = environment
        self.kwargs = kwargs
        self._closed = False

        # Load logger
        if recipe is not None:
            self.logger = recipe.logger
        else:
            from builder.utils.logger import global_logger
            self.logger = global_logger
    
    def _start_shell(self,
                     *,
                     use_fakeroot: bool = False,
                     cwd: str | Path | None = None) -> subprocess.Popen[str]:
        """Start a shell with a private channel for exit statuses."""

        command = [ "sh" ]

        if use_fakeroot:
            command.insert(0, "fakeroot")
        
        shell_loop = (
            "while IFS= read -r __runner_line; do\n"
            '   eval "$__runner_line"\n'
            "done\n"
        )

        process = subprocess.Popen(
            [ "sh", "-c", shell_loop ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            env=self.environment.as_dict(),
            cwd=Path(cwd) if cwd is not None else None,
            **self.kwargs
        )

        return process

    def _stop_shell(self) -> None:
        """Stop and release the current shell"""
        shell = self._shell_cache
        self._shell_cache = None

        if shell is None:
            return
        
        # Terminate shell
        if shell.poll() is None:
            shell.terminate()

            try:
                shell.wait(timeout=2)
            except subprocess.TimeoutExpired:
                shell.kill()
                shell.wait()
        
        # Close pipes
        if shell.stdin is not None:
            shell.stdin.close()
        
        if shell.stdout is not None:
            shell.stdout.close()
    
    def close(self) -> None:
        """Close the runner and its persisntent shell."""

        if self._closed:
            return
        
        self._closed = True
        self._stop_shell()

    @property
    def _shell(self) -> subprocess.Popen[str]:
        """Returns the shell used to execute commands

        Returns:
            subprocess.Popen[str]: The shell process.
        """
        if self._closed:
            raise ValueError("Runner is closed!")

        if self._shell_cache is not None:
            if self._shell_cache.poll() is None:
                return self._shell_cache

            self._shell_cache = None
        
        shell = self._start_shell(use_fakeroot=False)

        if self.persistent:
            self._shell_cache = shell

        return shell

    def run(
            self,
            cmd: str | list[str],
            *,
            check: bool = True,
            cwd: str | Path | None = None,
            timeout: float | None = None,
            silent: bool = False
    ) -> subprocess.CompletedProcess[str]:
        """Execute a command and return its completed-process result.

        Args:
            cmd (list[str]): Command and arguments to execute.
            check (bool, optional): Raises RuntimeError if the command exits unsuccessfully.
            recipe (BuildRecipe | None, optional): Optional recipe whose logger and information will be made available in the environment.
            cwd (str | Path | None, optional): Optional working directory for the subprocess.
            silent (bool): Disables logging of the invoked commands.
        """
        if self._closed:
            raise ValueError("Runner is closed!")
        
        script = cmd if isinstance(cmd, str) else "\n".join(cmd)

        if not script.strip():
            raise ValueError("Cannot execute an empty command.")

        if not silent:
            self.logger.debug(f"> {script}")

        with tempfile.TemporaryDirectory(prefix="cmd-") as tmp:
            dir = Path(tmp)
            script_file = dir / "script.sh"
            stdout_file = dir / "stdout"
            stderr_file = dir / "stderr"

            script_file.write_text(script)

            invocation = []

            # Add cd to invocation to respect cwd changes
            if cwd is not None:
                invocation.extend([
                    "__runner_old_pwd=$PWD",
                    f"cd {shlex.quote(os.fspath(cwd))}",
                    "__runner_cd_status=$?",
                    (
                        'if [ "$__runner_cd_status" -ne 0 ]; then '
                        '__runner_status=$__runner_cd_status; '
                        'else '
                    )
                ])

            # Create invocation of the main script
            invocation.extend([
                (
                    f". {shlex.quote(str(script_file))} "
                    f"</dev/null "
                    f"> {shlex.quote(str(stdout_file))} "
                    f"2> {shlex.quote(str(stderr_file))}"
                ),
                "__runner_status=$?",
            ])

            if cwd is not None:
                invocation.extend([
                    'cd "$__runner_old_pwd"',
                    "fi"
                ])
            
            # Dump status
            invocation.append('printf "%s\\n" "$__runner_status"')

            # Get shell
            shell = self._shell
            if shell.stdin is None or shell.stdout is None:
                raise RuntimeError("Shell pipes are unavailable.")
            
            try:
                # Write to shell
                shell.stdin.write(" ; ".join(invocation).replace("else  ; ", "else ") + "\n")
                shell.stdin.flush()

                # Handle timeouts
                ready, _, _ = select.select(
                    [ shell.stdout ],
                    [], [],
                    timeout
                )

                if not ready:
                    raise subprocess.TimeoutExpired(
                        cmd=script,
                        timeout=timeout or 10
                    )
                
                status_line = shell.stdout.readline()

                if not status_line:
                    raise RuntimeError("Shell exited before returning the command status.")

                returncode = int(status_line.strip())
            
            except (BrokenPipeError, ValueError, OSError, RuntimeError, subprocess.TimeoutExpired):
                self._stop_shell()
                raise

            result = subprocess.CompletedProcess(
                args=script,
                returncode=returncode,
                stdout=(
                    stdout_file.read_text(encoding="utf-8", errors="replace")
                    if stdout_file.exists() else ""
                ),
                stderr=(
                    stderr_file.read_text(encoding="utf-8", errors="replace")
                    if stderr_file.exists() else ""
                ),
            )

            if check and result.returncode != 0:
                raise subprocess.CalledProcessError(
                    returncode=returncode,
                    cmd=script,
                    output=result.stdout,
                    stderr=result.stderr
                )
            
            return result
    
    def __enter__(self) -> "Shell":
        if self._closed:
            raise RuntimeError("Shell is closed!")

        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()