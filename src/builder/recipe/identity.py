from typing import TYPE_CHECKING, Any

import json
import hashlib
import datetime
from pathlib import Path
from dataclasses import dataclass

if TYPE_CHECKING:
    from .recipe import (
        BuildRole,
        BuildRecipe,
    )

@dataclass(frozen=True, slots=True)
class BuildIdentity():
    """
    Stable identity of a particular package build.
    """

    name: str
    version: str
    role: "BuildRole"
    build_info: dict[str, str]

    @classmethod
    def create(cls, recipe: "BuildRecipe"):
        """Construct a new build identity from a recipe.

        Args:
            recipe (BuildRecipe): The recipe to construct the identity for.
        """

        # Get build-system arguments
        config_args = recipe._config_args(recipe.ctx)
        build_args = None
        install_args = None

        if recipe.build_system:
            config_args += (recipe.build_system.config_args or [])
            build_args = (recipe.build_system.build_args or [])
            install_args = (recipe.build_system.install_args or [])

        # Construct class
        return cls(
            name=recipe.metadata.name,
            version=recipe.metadata.version,
            role=recipe.build_role,
            build_info={
                "build_dir": str(recipe.ctx.build_dir),
                "build_arch": recipe.ctx.build_machine.arch,
                "target_arch": recipe.target.arch,
                "toolchain_dir": str(recipe.ctx.toolchain_dir),
                "toolchain_sysroot": str(recipe.ctx.toolchain_sysroot),
                "config_args": str(config_args),
                "build_args": str(build_args),
                "install_args": str(install_args),
            }
        )

    @property
    def target_type(self) -> str:
        """Return a custom target type of this build identity.

        A recipe of role ``TARGET`` may simply reuse the build outputs
        of a ``SYSROOT`` one and vice versa.
        """
        from .recipe import BuildRole
        match self.role:
            case BuildRole.SYSROOT | BuildRole.TARGET:
                return "target"
            
            case _:
                return self.role.name.lower()

    @property
    def fingerprint(self) -> str:
        """Return a deterministic, collision-resistant identity key representing
        this exact recipe.

        Returns:
            str: A sha256-hash of this identity.
        """
        h = hashlib.sha256()

        for key, value in self.build_info.items():
            h.update(f"{key}={value}".encode())

        return h.hexdigest()

class IdentityRegistry():
    """Track whether package build artifacts are reusable.

    Build records are keyed by ``BuildIdentity`` and contain the
    fingerprint of the configuration that produced the artifacts.

    A build is considered current only when its fingerprint matches
    the recorded one.
    """

    def __init__(self, metadata_dir: Path) -> None:
        self.metadata_dir = metadata_dir

    def metadata_file(self, identity: BuildIdentity) -> Path:
        """
        Return a unique metadata-file to record the passed built identity.
        """
        self.metadata_dir.mkdir(exist_ok=True, parents=True)
        return self.metadata_dir / f"{identity.name}.{identity.target_type}.json"

    def record(self, identity: BuildIdentity) -> None:
        """Record a recipe identity into its metadata file.

        Args:
            identity (BuildIdentity): The identity of the package build.
        """

        time = datetime.datetime.now()
        json.dump(
            {
                "info": identity.build_info,
                "fingerprint": identity.fingerprint,
                "timestamp_readable": str(time),
                "timestamp": str(datetime.datetime.timestamp(time)),
            },
            self.metadata_file(identity).open("w"),
            indent=4
        )
    
    def is_valid(self, identity: BuildIdentity) -> bool:
        """Check if a build identity is consistent with its
        recorded values.

        Args:
            identity (BuildIdentity): The identity to check.

        Returns:
            bool: ``True`` if the identity is consistent.
        """
        file = self.metadata_file(identity)
        
        if not file.exists():
            return False
        
        metadata: dict[str, Any] = json.load(file.open("r"))

        if not metadata:
            return False
        
        return metadata.get("fingerprint") == identity.fingerprint      

    def is_invalid(self, identity: BuildIdentity) -> bool:
        """Return true if the identity is inconsistent with its
        recorded values.

        Args:
            identity (BuildIdentity): The identity to check
        """
        return not self.is_valid(identity)

    def invalidate(self, identity: BuildIdentity) -> None:
        """Mark a recorded identity as invalid.

        This is achieved by removing the entry from the metadata-directory.

        Args:
            identity (BuildIdentity): The identity to invalidate
        """
        file = self.metadata_file(identity)
        if not file.is_file():
            return
        
        file.unlink(True)