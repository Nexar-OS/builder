from typing import Iterable
from builder.version.version import Version
from .source import VersionSource
from dataclasses import dataclass
import re
import requests

@dataclass
class WebVersionSource(VersionSource):
    """
    Discoveres software versions from a web resource using a regex expression.

    The regex expression passed is applied to the contents of the configured
    webpage.

    Attributes:
        url (str): The url of the upstream web-page.
        regex (str): The regex identifying the version string.
    """
    def __init__(self,
                 url: str,
                 regex: str
                ) -> None:
        self.url = url
        self.regex = re.compile(regex)
        self._webpage_content = None

    @property
    def webpage_content(self) -> str:
        """
        Fetch the content of the configured url.

        Returns:
            str: The content of the webpage.
        """
        if not self._webpage_content:
            response = requests.get(self.url)
            response.raise_for_status()

            self._webpage_content = response.text
        
        return self._webpage_content

    @property
    def versions(self) -> Iterable[Version]:
        """
        Retrieve and parse versions from the configured web resource.

        Returns:
            Iterable[Version]: A stream yielding all versions matching the configured regex.
        """
        found: set[Version] = set()

        for match in self.regex.finditer(self.webpage_content):
            raw = match.group("version")

            version = Version.from_version_string(raw)

            if not version:
                continue

            # Remove duplicates
            if version in found:
                continue

            found.add(version)

            yield version