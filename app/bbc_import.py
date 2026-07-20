import json
import re
from dataclasses import dataclass
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree


PAGE_HOSTS = {"bbc.co.uk", "www.bbc.co.uk"}
CAPTION_HOST_SUFFIXES = (".akamaized.net", ".bbci.co.uk")
MAX_PAGE_BYTES = 3 * 1024 * 1024
MAX_TTML_BYTES = 10 * 1024 * 1024
USER_AGENT = "BBC-TTML-Simple-Validator/1.0"


class BBCImportError(ValueError):
    pass


@dataclass(frozen=True)
class BBCImport:
    page_url: str
    programme_pid: str
    version_pid: str
    title: str
    orientation: str | None
    subtitles_url: str
    ttml: str


def _read(url: str, limit: int, accept: str) -> tuple[bytes, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    with urlopen(request, timeout=15) as response:
        data = response.read(limit + 1)
        final_url = response.geturl()
    if len(data) > limit:
        raise BBCImportError("The BBC response was larger than the allowed import limit.")
    return data, final_url


def _bbc_page_url(raw_url: str) -> str:
    parsed = urlparse(raw_url.strip())
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in PAGE_HOSTS:
        raise BBCImportError("Enter an https://www.bbc.co.uk page URL.")
    if not parsed.path.startswith(("/news/", "/iplayer/")):
        raise BBCImportError("This version supports BBC News and BBC iPlayer pages.")
    return parsed._replace(fragment="").geturl()


def _extract_page_media(page: str) -> tuple[str, str, str, str | None]:
    item = re.search(
        r'\\"media\\":\{.{0,8000}?\\"pid\\":\\"([a-z0-9]{8})\\"'
        r'.{0,8000}?\\"id\\":\\"([a-z0-9]{8})\\",\\"idType\\":\\"versionID\\"'
        r'.{0,1000}?\\"title\\":\\"(.*?)\\"',
        page,
        re.DOTALL,
    )
    if not item:
        raise BBCImportError("No playable BBC media version was found on that page.")
    programme_pid, version_pid, escaped_title = item.groups()
    try:
        title = json.loads(f'"{escaped_title}"')
    except json.JSONDecodeError:
        title = escaped_title.replace('\\"', '"')
    nearby = page[item.start():item.end() + 2000]
    orientation_match = re.search(r'\\"orientation\\":\\"(landscape|portrait)\\"', nearby)
    orientation = orientation_match.group(1) if orientation_match else None
    return programme_pid, version_pid, title, orientation


def _caption_url(media_selector: dict) -> str:
    for media in media_selector.get("media", []):
        if media.get("kind") != "captions":
            continue
        https_connections = [
            connection.get("href", "") for connection in media.get("connection", [])
            if connection.get("protocol") == "https"
        ]
        if https_connections:
            return https_connections[0]
    raise BBCImportError("This BBC media version does not expose TTML captions.")


def import_bbc_ttml(raw_url: str) -> BBCImport:
    page_url = _bbc_page_url(raw_url)
    page_bytes, final_page_url = _read(page_url, MAX_PAGE_BYTES, "text/html")
    if (urlparse(final_page_url).hostname or "").lower() not in PAGE_HOSTS:
        raise BBCImportError("The BBC page redirected outside the supported site.")
    page = page_bytes.decode("utf-8", errors="replace")
    programme_pid, version_pid, title, orientation = _extract_page_media(page)
    selector_url = (
        "https://open.live.bbc.co.uk/mediaselector/6/select/version/2.0/"
        f"mediaset/pc/vpid/{quote(version_pid)}/format/json"
    )
    selector_bytes, _ = _read(selector_url, MAX_PAGE_BYTES, "application/json")
    try:
        subtitles_url = _caption_url(json.loads(selector_bytes))
    except json.JSONDecodeError as exc:
        raise BBCImportError("BBC Media Selector returned an invalid response.") from exc
    caption_host = (urlparse(subtitles_url).hostname or "").lower()
    if urlparse(subtitles_url).scheme != "https" or not caption_host.endswith(CAPTION_HOST_SUFFIXES):
        raise BBCImportError("BBC Media Selector returned an unsupported caption location.")
    ttml_bytes, _ = _read(subtitles_url, MAX_TTML_BYTES, "application/ttml+xml, application/xml")
    try:
        ElementTree.fromstring(ttml_bytes)
    except ElementTree.ParseError as exc:
        raise BBCImportError("The downloaded caption resource is not valid XML.") from exc
    return BBCImport(
        page_url=page_url,
        programme_pid=programme_pid,
        version_pid=version_pid,
        title=title,
        orientation=orientation,
        subtitles_url=subtitles_url,
        ttml=ttml_bytes.decode("utf-8-sig"),
    )
