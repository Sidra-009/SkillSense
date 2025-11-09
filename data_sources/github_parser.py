"""
Simple GitHub profile fetcher: uses public GitHub user profile & readme of pinned repos.
This version uses unauthenticated requests; for production use OAuth and caching.
"""
import requests
from bs4 import BeautifulSoup

GITHUB_USER_URL = "https://github.com/{username}"

def parse_github_profile(username: str) -> str:
    if not username:
        return ""
    try:
        r = requests.get(GITHUB_USER_URL.format(username=username), timeout=6)
        if r.status_code != 200:
            return ""
        soup = BeautifulSoup(r.text, "html.parser")
        # pull bio, repo names, repo descriptions
        bio = soup.find("div", {"class":"p-note"})
        bio_text = bio.get_text(separator=" ", strip=True) if bio else ""
        repo_texts = []
        # collect repository names and descriptions from page (first page)
        for repo in soup.select("li[itemprop='owns']"):
            name = repo.find("a", {"itemprop":"name codeRepository"})
            desc = repo.find("p", {"itemprop":"description"})
            repo_texts.append((name.get_text(strip=True) if name else "", desc.get_text(strip=True) if desc else ""))

        combined = bio_text + "\n" + "\n".join([" ".join(r) for r in repo_texts])
        return combined.strip()
    except Exception:
        return ""
