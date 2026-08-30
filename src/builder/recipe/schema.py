from pathlib import Path
from pydantic import BaseModel, Field
from typing import Literal, Annotated, Union
from builder.recipe import BuildMethod
from builder.recipe import Dependencies

class Schema(BaseModel):
    ...

class AutotoolsSchema(Schema):
    type: Literal["autotools"]
    disable_fakeroot: bool = False
    skip_build: bool = False
    install_target: str = "autotools"
    config_args: list[str] | None = None
    build_args: list[str] | None = None
    install_args: list[str] | None = None

class CMakeSchema(Schema):
    type: Literal["cmake"]
    config_args: list[str] | None = None
    build_args: list[str] | None = None
    install_args: list[str] | None = None
    generator: str | None = None

class MesonSchema(Schema):
    type: Literal["meson"]
    disable_fakeroot: bool = False
    config_args: list[str] | None = None
    build_args: list[str] | None = None
    install_args: list[str] | None = None

class CustomBuildSystemSchema(Schema):
    type: Literal["custom"]
    prepare: str | None = None
    configure: str | None = None
    build: str | None = None
    install: str | None = None
    disable_fakeroot: bool = False

BuildSystemSchema = Annotated[
    Union[AutotoolsSchema, CMakeSchema, MesonSchema, CustomBuildSystemSchema],
    Field(discriminator="type")
]

class BuildSchema(Schema):
    method: BuildMethod
    build_system: BuildSystemSchema
    patches: list[Path] | None = None
    prepare: str | None = None
    post_install: str | None = None

class FileSourceSchema(Schema):
    type: Literal["file"]
    name: str
    url: str
    filename: str | None = None
    md5hash: str | None = None

class TarballSourceSchema(Schema):
    type: Literal["tarball"]
    name: str
    url: str
    filename: str | None = None
    md5hash: str | None = None
    strip_top_level: bool = True

SourceSchema = Annotated[
    Union[FileSourceSchema, TarballSourceSchema],
    Field(discriminator="type")
]

class RecipeSchema(Schema):
    name: str
    homepage: str
    license: str | list[str]
    description: str
    version: str
    dependencies: Dependencies | None = None
    sources: list[SourceSchema]
    build: BuildSchema