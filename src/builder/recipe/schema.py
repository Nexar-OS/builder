from pydantic import BaseModel
from builder.recipe import BuildMethod

class DependenciesSchema(BaseModel):
    required: list[str]
    optional: list[str]
    build: list[str]

class SourceSchema(BaseModel):
    type: str
    name: str
    url: str
    sha256: str

class BuildSystemSchema(BaseModel):
    type: str
    config_args: list[str] | None = None
    build_args: list[str] | None = None
    install_args: list[str] | None

class BuildSchema(BaseModel):
    method: BuildMethod
    build_system: BuildSystemSchema
    prepare: str | None = None
    post_install: str | None = None

class RecipeSchema(BaseModel):
    name: str
    homepage: str
    license: str
    description: str
    version: str
    dependencies: DependenciesSchema
    sources: list[SourceSchema]
    build: BuildSchema