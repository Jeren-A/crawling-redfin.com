from collections import defaultdict, deque
from typing import Set


class SiteMapManager:

    def __init__(self, base_url: str = None):
        self._base_url = base_url
        self._links = defaultdict(set)
        self._dead_links = set()
        self._assets = defaultdict(set)

    def get_outgoing_links(self, url: str) -> Set[str]:
        return self._links[url]

    def get_assets(self, url: str) -> Set[str]:
        return self._assets[url]

    def get_dead_links(self) -> Set[str]:
        return self._dead_links

    def get_base_url(self) -> str:
        return self._base_url

    def add_url_connection(self, url: str, outgoing_url: str) -> None:
        if not self._base_url: self._base_url = url
        self._links[url].add(outgoing_url)

    def add_dead_link(self, dead_link: str) -> None:
        self._dead_links.add(dead_link)
    
    def add_asset_connection(self, url: str, asset_link: str) -> None:
        if not self._base_url: self._base_url = url
        self._assets[url].add(asset_link)

    def _print_sitemap_helper(self, curr_link, curr_indent, indent=2):
        print((curr_indent * '-') + curr_link)

        if not self._assets[curr_link]:
            print('There is no assets for this link!')
        else:
            print('Assets:')
            for asset in self._assets[curr_link]:
                print(((curr_indent + indent) * '-') + asset)

        if not self._links[curr_link]:
            print('There is no outgoing links!')
        else:
            print('Outgoing Links:')
            for link in self._links[curr_link]:
                self._print_sitemap_helper(link, curr_indent + indent, indent=indent)

    def print_sitemap(self, indent=2) -> None:
        if not self._base_url:
            raise Exception('Cannot print the SiteMap as it does not have a base url!')
        self._print_sitemap_helper(self._base_url, 0, indent=indent)

    def print_dead_links(self):
        print('Dead links for this site:')
        print(*self._dead_links, sep='\n')


