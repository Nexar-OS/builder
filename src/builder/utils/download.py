from pathlib import Path
import requests

def download_url(url: str, dest: Path, chunk_size: int = 8192) -> None:
    """Download a file from a URL into a specific path on disk.

    Args:
        url (str): The url to download the file from.
        dest (Path): The final path where the file should be placed at (including filename).
    """
    response = requests.get(
        url,
        stream=True,
        timeout=(10, 60)
    )
    response.raise_for_status()

    with dest.open("wb") as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)