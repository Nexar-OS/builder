from typing import Iterable
from builder.version.version import Version
from .source import VersionSource
from dataclasses import dataclass
import re
import requests
from urllib.parse import quote

DEFAULT_BASE_URL = "https://gitlab.com"

@dataclass
class GitlabVersionSource(VersionSource):
    """
    Discoveres software versions from a gitlab repository.

    Attributes:
        repo (str): The github repository (Format: group/project)
        include_prereleases (bool): Whether prereleases should be included.
        base_url (str | None): Base URL of the GitLab instance. (Defaults to ``https://gitlab.com/``)
    """
    repo: str
    include_prereleases: bool = False
    base_url: str | None = None

    def _fetch_api(self):
        """
        Fetches the gitlab api response for ``/api/v4/projects/{repo}/releases``

        Returns:
            _type_: The reponse in json format.
        """
        project = quote(self.repo, safe="")
        url = (
            f"{self.base_url or DEFAULT_BASE_URL}/api/v4/projects/"
            f"{project}/releases"
        )

        params = {
            "per_page": 100
        }

        response = requests.get(
            url,
            params=params,
            timeout=(20, 60)
        )
        response.raise_for_status()

        return response.json()

    @property
    def versions(self) -> Iterable[Version]:
        """
        Retrieve and parse versions from GitLab releases.

        Returns:
            Iterable[Version]: A stream yielding all discovered versions.
        """
        json: list[dict] = self._fetch_api()
        found: set[Version] = set()

        for release in json:
            if release.get("upcoming_release"):
                continue

            tag = release.get("tag_name")
            if not tag:
                continue

            version = Version.from_version_string(tag)

            if version is None:
                continue

            if version in found:
                continue

            found.add(version)

            yield version