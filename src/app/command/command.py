from builder.build import BuildContext

from typing import (
    ClassVar,
    TypeVar,
    Generic,
    Any,
    Type
)

from argparse import (
    ArgumentParser,
    _SubParsersAction,
    Namespace,
    Action
)

from dataclasses import (
    dataclass,
    fields,
    field
)

from abc import (
    ABC,
    abstractmethod
)

T = TypeVar("T")
R = TypeVar("R")

@dataclass
class CLIArgument(Generic[T, R]):
    """
    Defune the configuration for a command-line argument.

    A ``CLIArgument`` describes how a dataclass field should be exposed as an
    argparse argument.

    Attributes:
        type (type[T]): The Python type used to parse the argument value.
        help (str): Help text displayed by argparse.
        flags (tuple[str, ...]): Command-line flags associated with the argument.
        positional (bool): Whether the argument should accept positional values.
    """

    def __init__(self,
                 type: type[T],
                 help: str,
                 flags: tuple[str, ...] = tuple(),
                 positional: bool = False,
                 **kwargs
                ):
        self.type = type
        self.help = help
        self.flags = flags
        self.positional = positional
        self.additional = kwargs

    def arg(self, parse: Type[R] | None = None) -> R:
        """
        Create a dataclass field configuration with this CLI argument.

        Args:
            parse (Type[R] | None, optional): Optional callable used as the dataclass field's
                                              ``default_factory``. Defaults to ``self.type``.

        Returns:
            R: A configured dataclass field
        """
        return field(
            default_factory=parse or self.type,
            metadata={
                "arg": self
            }
        )

    @property
    def kwargs(self) -> dict[str, Any]:
        """
        Returns the argpars keyword arguments for this argument.

        Returns:
            dict[str, Any]: A dictionary suitable for unpacking into
                            ``ArgumentParser.add_argument()``
        """
        kwargs: dict[str, Any] = {
            **self.additional,
            "help": self.help
        }

        if self.type is bool:
            kwargs["action"] = "store_true"
        else:
            kwargs["type"] = self.type

        if self.positional:
            kwargs["nargs"] = "*"
        
        return kwargs

@dataclass
class CLICommand(ABC):
    """
    Base class for commands exposed through a command-line interface.

    Subclasses define their command name and arguments required.
    """
    name: ClassVar[str]

    @classmethod
    def _populate_parser(cls, parser: ArgumentParser) -> None:
        """
        Register the command's CLIArguments with an argparse parser.

        Args:
            parser (ArgumentParser): The parser to populate.
        """
        for field in fields(cls):
            metadata = field.metadata
            
            if "arg" not in metadata:
                continue

            argument: CLIArgument = metadata["arg"]

            parser.add_argument(
                *argument.flags,
                dest=field.name,
                **argument.kwargs
            )

    @classmethod
    def add_to_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        """
        Add this command as a subcommand to an argparse parser.

        The command's name is used as the subparser name, and the command
        class is stored in the parsers defaults so that the parsed namespace
        can later be converted into an instance of this command.

        Args:
            subparsers (_SubParsersAction): The subparser collection to add this command to.
        """
        parser: ArgumentParser = subparsers.add_parser(
            name=cls.name
        )

        # Store parsed data in command class
        parser.set_defaults(command_class=cls)

        cls._populate_parser(parser)

        return parser

    @classmethod
    def from_namespace(cls, namespace: Namespace):
        """
        Create a command instance from an argparse namespace.

        Args:
            namespace (Namespace): The argparse namespace containing parsed
                                   command arguments.
        """

        values = vars(namespace)

        return cls(
            **{
                field.name: values[field.name]
                for field in fields(cls)
                if field.name in values
            }
        )
    
    def handle(self, ctx: BuildContext):
        """
        Execute the command.

        Subclasses must implement this method with the behavior that should
        occur when the command is invoked.
        """
        raise NotImplementedError