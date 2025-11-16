import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DeepKlarityBot/1.0)"}

def scrape_wikipedia(url: str) -> dict:
    """Return {'title': str, 'clean_text': str, 'raw_html': str, 'sections': List[str]}"""
    parsed = urlparse(url)
    if not parsed.scheme:
        raise ValueError("URL must include scheme (https://)")

    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("h1", id="firstHeading")
    title = title_tag.get_text(strip=True) if title_tag else url

    content = soup.find(id="mw-content-text")
    if not content:
        clean_text = soup.get_text(separator="\n", strip=True)
        return {"title": title, "clean_text": clean_text, "raw_html": html, "sections": []}

    # Remove certain tags that introduce noise
    for tag in content.find_all(["table", "sup", "style", "script"]):
        tag.decompose()

    sections = []
    clean_parts = []
    for child in content.find_all(['h2', 'h3', 'p']):
        if child.name in ['h2', 'h3']:
            heading = child.get_text(strip=True)
            sections.append(heading)
        elif child.name == 'p':
            text = child.get_text(strip=True)
            if text:
                clean_parts.append(text)

    clean_text = "\n\n".join(clean_parts)
    return {"title": title, "clean_text": clean_text, "raw_html": html, "sections": sections}
