from pathlib import Path
from collections.abc import Mapping
from typing import Any, TypeVar
from builder.utils.logger import warn
from yaml import safe_load
from yaml.parser import ParserError

T = TypeVar("T")


def retrieve_nested(
    data: Any,
    path: str|list[str],
    expected_type: type[T] | None = None,
    default: T | None = None
) -> T | None:
    """
    Retrieve a value from a nested mapping using a path.

    Each component of ``path`` is used as a key to traverse the nested mappings.

    Args:
        data (Any): The mapping to traverse.
        path (str | list[str]): The path to the desired value.
        expected_type (type[T] | None, optional): The type the value the retrieved
                                                  value should have.
        default (T | None, optional): Value to return if the path does not
                                      exist or the value has an unexpected type. Defaults to None.

    Returns:
        _type_: The expected type or ``None``.
    """
    current = data

    path = [ path ] if isinstance(path, str) else path
    for part in path:
        if not isinstance(current, Mapping):
            warn(
                f"cannot access '{part}' in '{path}': "
                f"expected a mapping, got {type(current).__name__}."
            )

            return default

        if part not in current:
            warn(f"path '{path} does not exist.'")
            return default

        current = current[part]

    if expected_type is not None and not isinstance(current, expected_type):
        warn(
            f"path '{path}' has type "
            f"{type(current).__name__}, expected {expected_type.__name__}."
        )
        return default
    
    return current


def load_yaml(path: Path) -> Any | None:
    """
    Safe loads a yaml file.

    Invokes the pyyaml ``safe_load`` function.

    Args:
        path (Path): The path to the yaml file.

    Returns:
        Any: The decoded content.
    """
    if not path.is_file():
        warn(f"Failed to load yaml from '{path}': File not found.")
        return None

    try:
        return safe_load(path.open("r"))
    except ParserError as e:
        warn(
            f"Failed to parse yaml from file '{path}':\n"
            f"{e}"
        )
        return None