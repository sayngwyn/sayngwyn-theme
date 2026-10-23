"""Build realistic local mocks of the theme's Nexus page and GitHub README, to check before release.

    py -3.12 pages/mock_pages.py

Nexus: fetches a live sayngwyn mod page (Creations Browser, same "site" layout) for Nexus's real markup and
stylesheets, removes its scripts, and swaps in this theme's title, header, gallery, tags and description. The
description is converted from pages/page.bbcode the way Nexus converts BBCode (read off a live page:
[center] -> <div align="center">, [size=N] -> <font size="N">, lists -> <ul class="disc">, images in
<div class="img-wrapper">, line breaks -> <br>). Images point at the local files, including the More-by
buttons that will live on sayngwyn.com. Needs internet for Nexus's own CSS and fonts.

GitHub: renders README.md through GitHub's own Markdown API (``gh api markdown``, as on the repo page) and
wraps it in GitHub's Markdown CSS, light and dark.

Writes dist/mock/nexus.html, dist/mock/github-dark.html and dist/mock/github-light.html.
"""

import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "mock"
UP = ROOT / "dist" / "nexus-upload"
LIVE = "https://www.nexusmods.com/site/mods/2483"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36"
TITLE = "Sayngwyn Theme for Mod Organizer 2"

PAGE = UP / "page"
IMAGES = {  # {IMG:key} in page.bbcode -> local file (on Nexus: hosted on sayngwyn.com)
    "divider": PAGE / "divider-v1.png",  # local copy, stands in for hosted divider-v4
    **{f"strip-{s}": PAGE / f"strip-{s}-v1.png" for s in ("how-it-looks", "what-you-get", "install", "good-to-know")},
    "mod-list": UP / "shots" / "mod-list.png",
    "run-area": UP / "shots" / "run-area.png",
}
# The gallery holds the first image and the real screenshots only (page v3).
GALLERY = [UP / "primary.png", IMAGES["mod-list"], IMAGES["run-area"]]


def url(path: Path) -> str:
    """The image embedded as a data URI, so the mock works anywhere (file pages, previews) as one file."""
    import base64
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def bbcode_to_nexus(src: str) -> str:
    s = html.escape(src, quote=False)
    s = re.sub(r"\[url=(.+?)\](.+?)\[/url\]", r'<a href="\1">\2</a>', s)
    s = re.sub(r"\[img\](.+?)\[/img\]", r'<div class="img-wrapper "> <img src="\1"> </div>', s)
    s = re.sub(r"\[size=(\d)\]", r'<font size="\1">', s).replace("[/size]", "</font>")
    s = s.replace("[b]", "<strong>").replace("[/b]", "</strong>").replace("[i]", "<em>").replace("[/i]", "</em>")
    s = s.replace("[center]", '<div align="center">').replace("[/center]", "</div>")
    s = re.sub(r"\[list=1\]\n?", '<ul class="content_list content_list_ordered">', s)
    s = re.sub(r"\[list\]\n?", '<ul class="disc">', s)
    s = re.sub(r"\n?\[/list\]", "</ul>", s)
    s = re.sub(r"\[\*\](.*?)(?=\n\[\*\]|</ul>)", r"<li>\1</li>", s, flags=re.S)
    s = re.sub(r"</li>\n<li>", "</li><li>", s)
    return s.replace("\n", "<br>")


def nexus() -> None:
    # Fetched once and cached: Nexus's bot protection turns away Python's client (403) and repeated fetches.
    cache = ROOT / "dist" / "mock-cache" / "nexus-live.html"
    if not cache.exists() or "--refresh" in sys.argv:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(subprocess.run(["curl", "-s", "--fail", "-A", UA, LIVE], capture_output=True,
                                         check=True, timeout=60).stdout)
    page = cache.read_text(encoding="utf-8")
    page = re.sub(r"<script\b.*?</script>", "", page, flags=re.S | re.I)
    page = re.sub(r"<iframe\b.*?</iframe>", "", page, flags=re.S | re.I)
    page = page.replace("<head>", '<head><base href="https://www.nexusmods.com/">', 1)
    page = page.replace("Creations Browser for Mod Organizer 2", TITLE)
    page = page.replace("Mod Organizer 2 Plugins", "Mod Organizer 2 Themes")
    # header image
    page = re.sub(r'(<div class="img-wrapper header-img ">\s*<img src=")[^"]+', r"\g<1>" + url(UP / "header.png"), page)
    # gallery strip
    thumbs = "".join(
        f'<li class="thumb" data-src="{url(p)}"><figure><a href="#"><img src="{url(p)}" alt=""></a></figure></li>'
        for p in GALLERY)
    page = re.sub(r'(<ul class="thumbgallery gallery clearfix">).*?(</ul>)', r"\g<1>" + thumbs.replace("\\", "\\\\") + r"\g<2>",
                  page, count=1, flags=re.S)
    # tags: the theme's
    page = page.replace("Quality of Life", "Visuals and Graphics")
    # the page summary ("About this mod") and the version
    summary = (ROOT / "reports" / "2026-10-22-release" / "summary.txt").read_text(encoding="utf-8")
    page = re.sub(r'(<h2 id="description_tab_h2"[^>]*>About this mod</h2>.*?<p>).*?(</p>)',
                  lambda m: m.group(1) + html.escape(summary) + m.group(2), page, count=1, flags=re.S)
    page = page.replace('<div class="stat">1.1.0</div>', '<div class="stat">1.0.0</div>')
    # description
    bb = (ROOT / "pages" / "page.bbcode").read_text(encoding="utf-8")
    more = (UP / "more-by" / "more-by.bbcode").read_text(encoding="utf-8")
    more = re.sub(r"https://sayngwyn\.com/img/mods/([a-z0-9-]+\.png)",
                  lambda m: url(UP / "more-by" / m.group(1)), more)
    bb = bb.replace("{BLOCK:MORE_BY}", more.strip())
    bb = re.sub(r"\{IMG:([a-z0-9-]+)\}", lambda m: url(IMAGES[m.group(1)]), bb)
    desc = bbcode_to_nexus(bb)
    start = page.index('<div class="container mod_description_container condensed">')
    inner = start + len('<div class="container mod_description_container condensed">')
    depth, i = 1, inner
    while depth:
        nxt = re.search(r"<div\b|</div>", page[i:])
        depth += 1 if nxt.group(0) == "<div" else -1
        i += nxt.end()
    page = page[:inner] + "\n" + desc + "\n</div>" + page[i:]
    (OUT / "nexus.html").write_text(page, encoding="utf-8")


def github() -> None:
    md = (ROOT / "README.md").read_text(encoding="utf-8")
    body = subprocess.run(["gh", "api", "markdown", "-f", f"text={md}", "-f", "mode=markdown",
                           "-f", "context=sayngwyn/sayngwyn-theme"],
                          capture_output=True, text=True, encoding="utf-8", check=True).stdout
    # GitHub serves docs/... from the repo; embed the local copies instead (matched by path)
    body = re.sub(r'(src|srcset)="[^"]*?(docs/[^"]+?\.png)"',
                  lambda m: f'{m.group(1)}="{url(ROOT / m.group(2))}"', body)
    base = ROOT.resolve().as_uri() + "/"
    for scheme, css, bg in (("dark", "github-markdown-dark.css", "#0d1117"),
                            ("light", "github-markdown-light.css", "#ffffff")):
        # GitHub picks the divider by the reader's theme; a mock page can't follow the OS, so pin each one.
        divider = url(ROOT / "docs" / ("divider.png" if scheme == "dark" else "divider-light.png"))
        body_s = re.sub(r"<picture>.*?</picture>", f'<img alt="" src="{divider}">', body, flags=re.S)
        doc = f"""<!doctype html><html><head><meta charset="utf-8"><base href="{base}">
<title>sayngwyn/sayngwyn-theme ({scheme})</title>
<meta name="color-scheme" content="{scheme}">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/{css}">
<style>body{{background:{bg};margin:0}} .markdown-body{{box-sizing:border-box;max-width:1012px;margin:32px auto;
padding:32px;border:1px solid {'#30363d' if scheme == 'dark' else '#d0d7de'};border-radius:6px}}</style></head>
<body><article class="markdown-body">{body_s}</article></body></html>"""
        (OUT / f"github-{scheme}.html").write_text(doc, encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    nexus()
    github()
    for f in sorted(OUT.iterdir()):
        print(f)


if __name__ == "__main__":
    main()
