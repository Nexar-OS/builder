from dataclasses import dataclass

@dataclass
class Dependencies:
    """
    Describes the dependencies required to build and use a recipe.

    Attributes:
        required: Dependencies required at runtime.
        optional: Dependencies that may be used but are not required.
        build: Dependnecies required (only) during the build process.
    """

    required: list[str]
    optional: list[str]
    build: list[str]
    
    @classmethod
    def none(cls):
        """
        Create an empty dependency declaration.

        Returns:
            Dependency: A Dependencies instance with all dependency lists empty.
        """
        return Dependencies(
            required=[],
            optional=[],
            build=[],
        )