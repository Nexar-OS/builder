from pathlib import Path
import requests
import time
from urllib.request import urlopen

def download_url(
        url: str,
        dest: Path,
        chunk_size: int = 8192,
        max_retries: int = 3,
        timeout: tuple[int, int] = (20, 60)
    ) -> None:
    """Download a file from a URL into a specific path on disk.

    Args:
        url (str): The url to download the file from.
        dest (Path): The final path where the file should be placed at (including filename).
        chunk_size (int): The size of chunks streamed into a file.
        max_retries (int): The maximum amount of retries on failed connections.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                stream=True,
                timeout=timeout
            )
        
            response.raise_for_status()

            with dest.open("wb") as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
            
            return
        
        except requests.RequestException:
            if attempt == max_retries - 1:
                raise

            time.sleep(2 ** attempt)

def url_file_to_md5(url: str) -> str | None:
    """Generate an md5hash of a file on a server.

    Args:
        url (str): The url pointing to the file to hash.

    Returns:
        str | None: The hash. None if file doesn't exist.
    """
    from builder.utils.data import calculcate_md5
    with urlopen(url) as response:
        return calculcate_md5(iter(lambda: response.read(8912), b""))