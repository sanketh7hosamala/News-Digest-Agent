import json
import logging
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from mcp.server.mcpserver import MCPServer

logging.getLogger("mcp").setLevel(logging.WARNING)

PROMPT_PATH = (
    Path(__file__).resolve().parent
    / "prompts"
    / "system_instructions.md"
)
UA = "Mozilla/5.0 (compatible; PersonalNewsAgent/1.0)"

# Create an MCP server
mcp = MCPServer(
    name="News-Digest-Tools"
)


def load_configured_hosts() -> set[str]:
    instructions = PROMPT_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"^## Configured sources\s*$([\s\S]*?)(?=^## |\Z)",
        instructions,
        re.MULTILINE,
    )
    if not match:
        raise ValueError(f"Missing '## Configured sources' in {PROMPT_PATH}")

    urls = re.findall(r"https?://[^\s)]+", match.group(1))
    hosts = {
        parsed.hostname.lower().removeprefix("www.")
        for url in urls
        if (parsed := urlparse(url)).hostname
    }
    if not hosts:
        raise ValueError(f"No valid source URLs found in {PROMPT_PATH}")

    return hosts


CONFIGURED_HOSTS = load_configured_hosts()


def is_configured_source(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().removeprefix("www.")
    return (
        parsed.scheme in {"http", "https"}
        and any(host == base or host.endswith("." + base) for base in CONFIGURED_HOSTS)
    )


def fetch_url(url: str) -> str:
    """Fetch a page from a source listed in system_instructions.md."""
    if not is_configured_source(url):
        allowed = ", ".join(sorted(CONFIGURED_HOSTS))
        return f"Error: URL is not on a configured news source. Allowed hosts: {allowed}"

    try:
        response = requests.get(
            url,
            #headers={"User-Agent": UA},
            headers={# Replace with the User-Agent string from your own browser.
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return f"Error fetching {url}: {exc}"

    content_type = response.headers.get("content-type", "")
    if "xml" in content_type or response.text.lstrip().startswith(
        ("<?xml", "<rss", "<feed")
    ):
        return response.text[:30000]

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "aside", "form", "noscript"]):
        tag.decompose()

    links: list[str] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        text = anchor.get_text(" ", strip=True)
        href_value = anchor.get("href")
        if not isinstance(href_value, str):
            continue

        href = urljoin(url, href_value)
        if len(text) >= 25 and href not in seen and is_configured_source(href):
            seen.add(href)
            links.append(f"{text} -> {href}")

        if len(links) >= 80:
            break

    body = soup.find("article") or soup.find("main") or soup.body or soup
    text = " ".join(body.get_text(" ", strip=True).split())
    title = soup.title.get_text(strip=True) if soup.title else ""

    return json.dumps(
        {"title": title, "text": text[:6000], "links": links},
        ensure_ascii=False,
    )


mcp.add_tool(
    fn=fetch_url,
    name="fetch_url",
    description=(
        "Fetch an article or feed from a news source listed in the configured "
        "sources section of system_instructions.md."
    ),
)

if __name__ == "__main__":
    mcp.run(transport="stdio")