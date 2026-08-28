from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union
from builder.recipe import BuildMethod
from builder.recipe import Dependencies

class BuildSystemSchema(BaseModel):
    type: str
    config_args: list[str] | None = None
    build_args: list[str] | None = None
    install_args: list[str] | None = None

class BuildSchema(BaseModel):
    method: BuildMethod
    build_system: BuildSystemSchema
    prepare: str | None = None
    post_install: str | None = None

class FileSourceSchema(BaseModel):
    type: Literal["file"]
    name: str
    url: str
    filename: str|None = None
    md5hash: str|None = None

class TarballSourceSchema(BaseModel):
    type: Literal["tarball"]
    name: str
    url: str
    filename: str|None = None
    md5hash: str|None = None
    strip_top_level: bool = True

SourceSchema = Annotated[
    Union[FileSourceSchema, TarballSourceSchema],
    Field(discriminator="type")
]

class RecipeSchema(BaseModel):
    name: str
    homepage: str
    license: str
    description: str
    version: str
    dependencies: Dependencies
    sources: list[SourceSchema]
    build: BuildSchema