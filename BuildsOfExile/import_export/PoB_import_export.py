import base64
import zlib


def base64_to_xml(base64_str):
    compressed_bytes = base64.urlsafe_b64decode(base64_str)
    return zlib.decompress(compressed_bytes).decode('utf-8')


def xml_to_base64(xml):
    compressed_bytes = zlib.compress(xml.encode('utf-8'), level=9)
    return base64.urlsafe_b64encode(compressed_bytes).decode('utf-8')
