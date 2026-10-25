from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RETRYABLE_HTTP_STATUSES = {408, 425, 429, 500, 502, 503, 504}
MAX_ATTEMPTS = 3


def fetch_rss(url: str, user_agent: str) -> ET.Element:
    request = Request(url, headers={"User-Agent": user_agent})
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urlopen(request, timeout=30) as response:
                root = ET.fromstring(response.read())
            if root.find("channel") is None:
                raise ET.ParseError("RSS response is missing its channel element")
            return root
        except HTTPError as error:
            if error.code not in RETRYABLE_HTTP_STATUSES:
                raise
            failure = f"HTTP {error.code}: {error.reason}"
        except (URLError, TimeoutError, ET.ParseError) as error:
            failure = str(error)

        if attempt == MAX_ATTEMPTS:
            raise RuntimeError(
                f"Could not fetch a valid RSS feed from {url} after "
                f"{MAX_ATTEMPTS} attempts: {failure}"
            )

        delay = 2 ** (attempt - 1)
        print(
            f"RSS request failed ({failure}); retrying in {delay}s "
            f"({attempt}/{MAX_ATTEMPTS})."
        )
        time.sleep(delay)

    raise RuntimeError(f"Could not fetch RSS feed from {url}")
