"""
A very simple parser that extracts visible experience/skills sections from
a pasted LinkedIn profile HTML or text. For privacy & reliability, we don't
scrape LinkedIn; we just accept HTML/text pasted by the user.
"""
from bs4 import BeautifulSoup

def parse_linkedin_html(html_or_text: str) -> str:
    # if it's plain text, just return
    if "<" not in html_or_text:
        return html_or_text

    soup = BeautifulSoup(html_or_text, "html.parser")
    texts = []

    # common LinkedIn classes are unpredictable; just grab headings + paragraphs
    for tag in soup.find_all(["h1","h2","h3","h4","p","li","span","div"]):
        t = tag.get_text(separator=" ", strip=True)
        if t:
            texts.append(t)

    return "\n".join(texts)
