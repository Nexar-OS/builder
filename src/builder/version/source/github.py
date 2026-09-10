from typing import Iterable
from builder.version.version import Version
from .source import VersionSource
from dataclasses import dataclass
import re
import requests

@dataclass
class GithubVersionSource(VersionSource):
    """
    Discoveres software versions from a github repository.

    Versions are discovered from GitHub releases.

    Attributes:
        repo (str): The github repository (Format: user/name)
        include_prereleases (bool): Whether prereleases should be included.
    """
    repo: str
    include_prereleases: bool = False

    API_URL = "https://api.github.com"

    def __post_init__(self):
        if not re.fullmatch(
            r"[^/]+/[^/]+",
            self.repo
        ):
            raise ValueError("Repository must be in 'owner/name' format!")

    def _fetch_api(self):
        """
        Fetches the github api response for ``/repos/{repo}/releases``

        Returns:
            _type_: The reponse in json format.
        """

        headers = {
            "Accept": "application/vnd.github+json"
        }

        url = f"{self.API_URL}/repos/{self.repo}/releases"

        params = {
            "per_page": 100
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=(20, 60)
        )
        response.raise_for_status()

        return response.json()

    @property
    def versions(self) -> Iterable[Version]:
        """
        Retrieve and parse versions from the configured web resource.

        Returns:
            Iterable[Version]: A stream yielding all versions matching the configured regex.
        """
        json: list[dict] = self._fetch_api()

        found: set[Version] = set()

        for release in json:
            if release.get("draft"):
                continue

            if release.get("prerelease") and not self.include_prereleases:
                continue

            value = release.get("tag_name")

            if not value:
                continue

            version = Version.from_version_string(value)

            if version is None:
                continue

            if version in found:
                continue

            found.add(version)
            yield version