from pydantic import BaseModel

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
    method: str
    build_system: BuildSystem
    prepare: str | None = None
    post_install: str | None = None

class RecipeSchema(BaseModel):
    name: str
    homepage: str
    lisence: str
    description: str
    version: str
    dependencies: Dependencies
    sources: list[Source]
    build: Build