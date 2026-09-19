from .tarball import TarballExporter
from .debian import DebianExporter

EXPORTERS = {
    clazz.format: clazz

    for clazz in [
        TarballExporter,
        DebianExporter,

    ]
}