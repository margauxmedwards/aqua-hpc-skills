#!/usr/bin/env python3
"""Stage only the HTML guide and reviewed public references for Jekyll."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def html_links(text):
    # Guide source is HTML; only rewrite local Markdown anchors, not code samples.
    return re.sub(r'(href=")([^"#]+)\.md(#[^"]*)?(")', r'\1\2.html\3\4', text)


def markdown_links(text):
    # Our maintained references use inline Markdown links, with no external .md links.
    def rewrite(match):
        target = match.group(1)
        if '://' in target:
            return match.group(0)
        return '](' + re.sub(r'\.md(?=#|$)', '.html', target) + ')'
    return re.sub(r'\]\(([^)]+)\)', rewrite, text)


def prepare(destination):
    destination = Path(destination)
    if destination.exists():
        raise ValueError('Destination exists; use a fresh build directory')
    destination.mkdir(parents=True)
    for page in sorted((ROOT/'docs').glob('*.html')):
        name = page.name
        guide = page.read_text()
        guide = guide.replace('href="../', 'href="')
        guide = html_links(guide)
        # Published main uses the default branch; retain the draft tip only in local docs.
        guide = re.sub(r'<p class="small" id="checkout-note">.*?</p>',
                       '<p class="small">Clone the default branch.</p>',
                       guide, flags=re.S)
        (destination/name).write_text(guide)
    for name in ('guide.css', 'guide.js'):
        (destination/name).write_text((ROOT/'docs'/name).read_text())
    (destination/'_config.yml').write_text('title: Aqua field guide\nmarkdown: kramdown\nrelative_links:\n  enabled: false\nkramdown:\n  input: GFM\n  syntax_highlighter: rouge\n')
    layout = destination/'_layouts/reference.html'
    layout.parent.mkdir()
    layout.write_text('''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>{{ page.title | escape }} · Aqua field guide</title>
<style>:root{color-scheme:only light}body{font:17px/1.7 system-ui,sans-serif;max-width:900px;margin:40px auto;padding:0 24px;color:#172a37;background:#f7f8f4}a{color:#00675c}pre{background:#e7eeea;padding:16px;overflow:auto}code{font-size:.88em;overflow-wrap:anywhere}table{border-collapse:collapse;display:block;overflow:auto}td,th{padding:10px;border:1px solid #ccd6d0}h1,h2,h3{line-height:1.2}nav{margin-bottom:35px}a:focus-visible{outline:3px solid #b76000}img{max-width:100%}</style></head>
<body><nav><a href="{{ page.guide_path }}">← Aqua field guide</a></nav><main>{{ content }}</main></body></html>
''')
    sources = sorted((ROOT/'skills/aqua-hpc').rglob('*.md'))
    sources += [ROOT/'examples/matrix/README.md']
    sources += sorted((ROOT/'tests/behavior').rglob('*.md'))
    sources += [ROOT/'tests/behavior/scenarios.json']
    for source in sources:
        if source.is_symlink():
            raise ValueError(f'Refusing symlink: {source}')
        relative = source.relative_to(ROOT)
        target = destination/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        text = source.read_text()
        if source.suffix == '.md':
            if text.startswith('---\n'):
                text = text.split('---\n', 2)[2]
            heading = re.search(r'^# (.+)$', text, flags=re.M)
            title = heading.group(1) if heading else source.stem
            guide_path = '../' * len(relative.parent.parts) + 'index.html'
            text = ('---\nlayout: reference\ntitle: ' + json.dumps(title) +
                    '\nguide_path: ' + json.dumps(guide_path) + '\n---\n\n' + markdown_links(text))
        target.write_text(text)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=Path('_pages_source'))
    args = parser.parse_args()
    print(prepare(args.destination))


if __name__ == '__main__':
    main()
