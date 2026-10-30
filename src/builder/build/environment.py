import os
from pathlib import Path
import shutil

from typing import Mapping, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import StrEnum, auto

if TYPE_CHECKING:
    from .context import BuildContext
    from builder.toolchain import Toolchain


class EnvironmentProfile(StrEnum):
    """
    Identify the intended purpose of a subprocess environment.
    """

    NATIVE = auto()

    HOST_TOOLS = auto()

    TARGET = auto()

# Variables that MUST NOT leak from one package-discovery configuration
# into another one.
_PKG_CONFIG_VARIABLES = (
    "PKG_CONFIG",
    "PKG_CONFIG_SYSROOT_DIR",
    "PKG_CONFIG_LIBDIR",
)

# Compiler variables commonly inherited by build systems.
_COMPILER_VARIABLES = (
    "CC", "CPP", "CXX", "AR", "AS", "LD", "NM", "RANLIB", "STRIP",
    "OBJCOPY", "OBJDUMP", "READELF", "OBJC",
    "CFLAGS", "CPPFLAGS", "CXXFLAGS", "LDFLAGS", "MAKEFLAGS",
    "ASFLAGS", "FCFLAGS", "MFLAGS", "GNUMAKEFLAGS", "F77", "F90"
)

# cross-aware build systems have their own host-compiler variables.
_HOST_VARIABLES = (
    "HOSTCC", "HOSTCPP", "HOSTCXX", "HOSTAR", "HOSTAS", "HOSTLD",
    "HOSTNM", "HOSTRANLIB", "HOSTSTRIP", "HOSTOBJCOPY", "HOSTOBJDUMP",
    "HOSTREADELF", "OBJC", "HOSTCFLAGS", "HOSTCPPFLAGS", "HOSTCXXFLAGS",
    "HOSTLDFLAGS", "HOSTLDLIBS", "HOSTPKG_CONFIG", "HOSTRUSTC", "CC_FOR_BUILD",
    "CXX_FOR_BUILD", "PKG_CONFIG_FOR_BUILD"
)

# Build-related variables which may otherwise leak from
# the invoking shell or from a previous configuration.
_BUILD_VARIABLES = (
    "SYSROOT",
    "CMAKE_TOOLCHAIN_FILE",
    "CMAKE_SYSROOT",
    "CMAKE_PREFIX_PATH",
    "CMAKE_FIND_ROOT_PATH",
    "CMAKE_INCLUDE_PATH",
    "CMAKE_FRAMEWORK_PATH"
    "PKG_CONFIG_ALLOW_SYSTEM_CFLAGS",
    "PKG_CONFIG_ALLOW_SYSTEM_LIBS",
)

def _native_tool(name: str) -> str:
    """
    Return the full native filesystem path of an executable
    according to the hosts environment $PATH variable.
    """
    return shutil.which(name) or name

@dataclass
class Environment:
    """
    Immutable snapshot of a subprocess environment.
    """
    profile: EnvironmentProfile
    variables: Mapping[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, str]:
        """Return a mutable copy suitable for `subprocess.run(env=...)`."""
        return dict(self.variables)
    
    def get(self, key: str, default: str | None = None) -> str | None:
        """Return an environment variable without exposing the mapping."""
        return self.variables.get(key, default)
    
    def derive(self,
               *,
               overrides: Mapping[str, str] | None = None,
               unset: tuple[str, ...] = ()) -> "Environment":
        """Create a new environment with command-specific modifications.

        This function does not modify the current instance of the environment.
        It will only construct a new, modified variant.

        Args:
            overrides (Mapping[str, str] | None, optional): Optioanl variables to add and/or override from the current environemnt. Defaults to None.
            unset (tuple[str, ...], optional): Optional variables to completely remove from the new environment. Defaults to ().

        Returns:
            Environment: A new and modified environment.
        """
        variables = self.as_dict()

        # Unset keys
        for key in unset:
            variables.pop(key, None)

        # Apply overrides
        if overrides:
            variables.update(overrides)

        return Environment(
            profile=self.profile,
            variables=variables
        )

    @classmethod
    def native(cls,
               *,
               inherit: bool = True) -> "Environment":
        """Construct an environment for native build-machine commands.

        The native environment uses the build machine's ordinary compiler
        and package discovery.

        Args:
            inherit (bool, optional): Whether to inherit the caller's general environment. Defaults to True.
        """

        variables = os.environ.copy() if inherit else {}

        # Remove inherited variables that might conflict.
        for key in (
            *_COMPILER_VARIABLES,
            *_PKG_CONFIG_VARIABLES,
            *_BUILD_VARIABLES,
            *_HOST_VARIABLES,
            "HOSTPKG_CONFIG"
        ):
            variables.pop(key, None)

        # Native tool discovery should use the build machine's $PATH
        variables.update({
            # Resolve build-machine tools now. Later, a staged
            # PATH might be added, so bare names could be shadowed.
            "CC": _native_tool("gcc"),
            "CXX": _native_tool("g++"),
            "AR": _native_tool("ar"),
            "AS": _native_tool("as"),
            "LD": _native_tool("ld"),
            "NM": _native_tool("nm"),
            "RANLIB": _native_tool("ranlib"),
            "STRIP": _native_tool("strip"),
            "OBJCOPY": _native_tool("objcopy"),
            "OBJDUMP": _native_tool("objdump"),
            "READELF": _native_tool("readelf"),
            "PKG_CONFIG": _native_tool("pkg-config"),
        })

        return cls(
            profile=EnvironmentProfile.NATIVE,
            variables=variables,
        )
    
    @classmethod
    def host_tools(cls,
                   ctx: "BuildContext",
                   *,
                   inherit: bool = True) -> "Environment":
        """Generate the environment for staged native host dependencies.

        Native executables and libraries are expected to be staged in
        `ctx.toolchain_host_tools`. This profile deliberately uses host-side
        package metadata rather than target sysroot metadata to prevent
        cross-compilation issues.
        """
        variables = cls.native(inherit=inherit).as_dict()

        prefix = Path(ctx.toolchain_host_tools)
        host_bin = prefix / "usr" / "bin"

        # Add host_bin to PATH.
        existing_path = variables.get("PATH", "")
        variables["PATH"] = os.pathsep.join(
            part for part in (str(host_bin), existing_path) if part
        )

        # Host-side runtime lookup, when needed, may use staged host
        # libraries.
        ld_library_path = variables.get("LD_LIBRARY_PATH", "")
        variables["LD_LIBRARY_PATH"] = os.pathsep.join(
            (
                *(
                    str(prefix / "usr" / "lib"),
                    str(prefix / "usr" / "lib64")
                ),
                *(
                    [ld_library_path] if ld_library_path
                    else []
                ),
            )
        )

        return cls(
            profile=EnvironmentProfile.HOST_TOOLS,
            variables=variables,
        )
    
    @classmethod
    def target(cls,
               toolchain: "Toolchain",
               *,
               inherit: bool = True) -> "Environment":
        """Construct an environment for cross-compilation.

        The compiler and sysroot come from the supplied toolcahin.
        Target pkg-config metadata is isolated to directories inside
        the toolchain's sysroot.
        
        Args:
            toolchain (Toolchain): Toolchain used for cc.
            inherit (bool, optional): Whether to inherit the caller's general environment. Defaults to True.
        """
        return cls.from_toolchain(
            toolchain=toolchain,
            profile=EnvironmentProfile.TARGET,
            inherit=inherit,
            target=True,
        )

    @classmethod
    def from_toolchain(
        cls,
        toolchain: "Toolchain",
        *,
        profile: EnvironmentProfile,
        inherit: bool = True,
        target: bool = False
    ) -> "Environment":
        """Construct an environment from an existing toolchain.

        This method bridges the Toolchain abstraction with the
        build Environments.

        Args:
            toolchain (Toolchain): Toolchain providing paths, flags and binaries.
            profile (EnvironmentProfile): Purpose associated with this environment.
            inherit (bool, optional): Whether to inherit the caller's general environment. Defaults to True.
            target (bool, optional): Whether to configure target-specific pkg-config isolation. (For cross-target environments.)
        """

        variables = os.environ.copy() if inherit else {}

        # Clean up environ
        for key in (
            # Never allow the caller's pkg-config settings to override the
            # package-discovery chosen for this toolchain.
            *_PKG_CONFIG_VARIABLES,
            *_HOST_VARIABLES,

            # Remove build flags inherited from native toolchain.
            *_COMPILER_VARIABLES,
            *_BUILD_VARIABLES
        ):
            variables.pop(key, None)
        
        # Apply the toolchain's configured environment first.
        variables.update(toolchain.env)

        if target:
            sysroot = Path(toolchain.sysroot)

            pkg_config_dirs = (
                sysroot / "usr" / "lib" / "pkgconfig",
                sysroot / "usr" / "lib64" / "pkgconfig",
                sysroot / "usr" / "share" / "pkgconfig",
                sysroot / "usr" / "lib" / "pkgconfig",
                sysroot / "usr" / "lib" / toolchain.target.triple / "pkgconfig",
            )

            variables["PKG_CONFIG_SYSROOT_DIR"] = str(sysroot)
            variables["PKG_CONFIG_LIBDIR"] = os.pathsep.join(
                str(path) for path in pkg_config_dirs
            )
            variables["PKG_CONFIG_PATH"] = ""

        return cls(
            profile=profile,
            variables=variables,
        )

    @classmethod
    def from_context(
        cls,
        ctx: "BuildContext",
        profile: EnvironmentProfile,
        *,
        inherit: bool = True
    ) -> "Environment":
        """Construct an environment using the build context.

        Args:
            ctx (BuildContext): Build context supplying machine, toolchain and prefix data.
            profile (EnvironmentProfile): Requested environment profile.
            inherit (bool, optional): Whether to inherit the caller's general environment. Defaults to True.
        
        Returns:
            (Environment): The environment for the requested profile.
        """
        match profile:
            case EnvironmentProfile.NATIVE:
                return cls.native(inherit=inherit)
            
            case EnvironmentProfile.HOST_TOOLS:
                return cls.host_tools(ctx, inherit=inherit)

            case EnvironmentProfile.TARGET:
                return cls.target(
                    toolchain=ctx.toolchain,
                    inherit=inherit
                )
        
            case _:
                raise ValueError(f"Unsupported environment profile: {profile!r}")
    
    def __repr__(self) -> str:
        import json
        return (
            f"Environment({self.profile.name.upper()}) " +
            json.dumps(
                self.as_dict(),
                indent=4
            )
        )