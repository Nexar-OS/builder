from tests.vars import ctx
from builder.recipe import BuildRole
from builder.version.source import *

vs = GitlabVersionSource(
    repo="xorg/lib/libpciaccess",
    base_url="https://gitlab.freedesktop.org/",
    identifier="repository/tags",
    note_filter="libpciaccess"
)

for v in vs.versions:
    print(v)

print("\n\nLatest:")

print(vs.latest_version)