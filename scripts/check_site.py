#!/usr/bin/env python3
"""Check that the built site has a landing page and no broken local HTML links."""
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])


def check(root):
    root = Path(root).resolve()
    assert (root/'index.html').is_file(), 'Missing landing page'
    documents = {}
    for path in root.rglob('*.html'):
        parser = Links()
        parser.feed(path.read_text())
        documents[path] = parser
    for path, parser in documents.items():
        for href in parser.links:
            url = urlsplit(href)
            if url.scheme or url.netloc:
                continue
            assert not url.path.startswith('/'), f'Root-relative link breaks project sites: {href}'
            target = (path.parent/unquote(url.path)).resolve() if url.path else path
            assert target.is_relative_to(root), f'Link leaves site: {href}'
            if target.is_dir():
                target /= 'index.html'
            assert target.is_file(), f'{path.relative_to(root)}: missing {href}'
            if url.fragment and target in documents:
                assert unquote(url.fragment) in documents[target].ids, f'Broken anchor: {href}'
    return len(documents)


if __name__ == '__main__':
    print(f'Validated links in {check(sys.argv[1])} HTML pages')
