import base64
import zlib

import requests

from BuildsOfExile.exceptions import PastebinImportException


def import_from_pastebin(url: str):
    parts = url.rsplit('/', maxsplit=1)
    if parts[0] != 'https://pastebin.com':
        raise PastebinImportException('Incorrect Pastebin URL - must start with "https://pastebin.com/"')
    final_url = parts[0] + '/raw/' + parts[1]
    response = requests.get(final_url)
    response.raise_for_status()
    return response.text


def base64_to_xml(base64_str):
    compressed_bytes = base64.urlsafe_b64decode(base64_str)
    return zlib.decompress(compressed_bytes).decode('utf-8')

