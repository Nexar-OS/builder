from dataclasses import dataclass

from builder.build import BuildContext
from builder.recipe import BuildRole
from .command import CLICommand, CLIArgument

@dataclass
class CheckCommand(CLICommand):
    name = "check"

    recipes: list[str] = CLIArgument(
        type=str,
        help="Pass one or multiple recipe(s) to build.",
        positional=True
    ).arg(parse=list[str])

    use_all: bool = CLIArgument(
        type=bool,
        help="Select all available recipes over all repositories passed to the registry.",
        flags=("--all", "-a")
    ).arg()

    only_outdated: bool = CLIArgument(
        type=bool,
        help="Only print outdated versions.",
        flags=("--only-outdated", "-o")
    ).arg()

    def handle(self, ctx: BuildContext):
        if self.use_all:
            recipe_names: list[str] = list(ctx.registry.all)
        else:
            recipe_names: list[str] = self.recipes
        
        recipes = [
            ctx.registry.getOrThrow(
                name=recipe,
                role=BuildRole.TARGET,
                ctx=ctx
            )
            for recipe in sorted(recipe_names)
        ]

        print(f"{'Recipe':<30} {'Current version':<20} {'Latest version':<20} {'Status':<15}")

        for recipe in recipes:
            version_source = recipe.version_source

            latest = "unknown"
            if version_source:
                try:
                    latest = version_source.latest_version.raw
                except KeyboardInterrupt:
                    raise
                except Exception:
                    ...

            is_outdated = False
            if not latest:
                status = "Failed."
            
            elif recipe.version == latest:
                status = "Up to date."
            
            else:
                is_outdated = True
                status = "Outdated!"

            if self.only_outdated and not is_outdated:
                continue

            print(
                f"{recipe.name:<30} "
                f"{recipe.version:<20} "
                f"{latest:<20} "
                f"{status:<15}"
            )