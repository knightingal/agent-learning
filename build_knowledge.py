from pathlib import Path
from urllib.parse import urlparse
import re
import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = Path(__file__).resolve().parent / "knowledge"
OUTPUT_DIR.mkdir(exist_ok=True)

def safe_name(url: str) -> str:
    path = urlparse(url).path.strip("/") or "index"
    name = re.sub(r"[^a-zA-Z0-9_-]+", "_", path)
    return name[:80] + ".md"

def fetch_main_text(url: str) -> str:
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": "AndroidFAQAgentLearningProject/1.0"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for node in soup(["script", "style", "nav", "footer", "header", "aside"]):
        node.decompose()

    main = soup.find("main") or soup.find("article") or soup.body
    if main is None:
        raise ValueError("No readable main content found")

    lines = [line.strip() for line in main.get_text("\n").splitlines()]
    return "\n".join(line for line in lines if line)

def save_url(url: str) -> Path:
    text = fetch_main_text(url)
    target = OUTPUT_DIR / safe_name(url)
    target.write_text(
        f"# Source\n\nSource URL: {url}\n\n# Extracted content\n\n{text}\n",
        encoding="utf-8",
    )
    return target

if __name__ == "__main__":
    urls = [
        # Add only documentation pages whose terms permit this use.
        # "https://example.com/documentation-page",
    ]
    for item in urls:
        print(save_url(item))
