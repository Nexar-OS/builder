from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from pathlib import Path

from builder.recipe import DependencyGraph, DependencyKind
from builder.build import BuildContext
from builder.recipe import BuildRole, BuildRecipe
from builder.package import *
from builder.package.export import *
from builder.utils.logger import error, warn
from .command import CLICommand, CLIArgument

@dataclass
class PackageCommand(CLICommand):
    name = "package"

    recipes: list[str] = CLIArgument(
        type=str,
        help="Pass one or multiple recipe(s) to export.",
        positional=True
    ).arg(parse=list[str])

    use_all: bool = CLIArgument(
        type=bool,
        help="Select all available recipes over all repositories passed to the registry.",
        flags=("--all", "-a")
    ).arg()

    with_dependencies: bool = CLIArgument(
        type=bool,
        help="Export all runtime dependencies of packages as well.",
        flags=("--with-deps", "-d")
    ).arg()

    export_path: Path | None = CLIArgument(
        type=Path,
        help="The path to put the exportet artifacts.",
        flags=("--export-path", "-e")
    ).arg()

    format: str = CLIArgument(
        type=str,
        help="The format to export to.",
        flags=("--format", "-f"),
        default="tarball"
    ).arg()

    def handle(self, ctx: BuildContext):
        exporter_class = EXPORTERS.get(self.format, None)
        if not exporter_class:
            error(
                f"Unknown format '{self.format}'! "
                + "Use one of the below: \n"
                + ", ".join(EXPORTERS.keys())
            )
            return
        
        exporter = exporter_class()

        if self.use_all:
            recipe_names: list[str] = list(ctx.registry.all)
        else:
            recipe_names: list[str] = self.recipes

        if not recipe_names:
            error("Please pass one or more recipes to package.")
        
        recipes = [
            ctx.registry.getOrThrow(
                name=recipe_name,
                role=BuildRole.TARGET,
                ctx=ctx
            )
            for recipe_name in recipe_names
        ]

        # Add runtime dependencies
        if self.with_dependencies:
            graph = DependencyGraph(
                recipes=recipes,
                registry=ctx.registry,
                kind=DependencyKind.RUNTIME,
                allow_cycles=True
            )
            
            recipes = list(
                graph.recipes.values()
            )

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    self._package_recipe,
                    recipe,
                    exporter,
                    self.export_path or ctx.build_dir / "exported"
                )

                for recipe in recipes
            ]

            for future in as_completed(futures):
                future.result()            
    
    def _package_recipe(self, recipe: BuildRecipe, exporter: PackageExporter, export_dir: Path):
        package = Package.from_recipe(recipe)

        if not package:
            warn(f"Cannot export recipe '{recipe.name}'. Recipe hasn't been built yet!")
            return

        artifact = exporter.export(
            package=package,
            destination=export_dir
        )
        
        print(f"Successfully packaged '{package.metadata.name}' into '{artifact.path}'")