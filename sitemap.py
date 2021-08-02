from collections import defaultdict, deque


class SiteMapManager:
    """
    TODO: Test this class
    TODO: Make this class thread safe
    """

    def __init__(self, base_url=None: str) -> None:
        self.base_url = base_url
        self.links = defaultdict(set)
        self.assets = defaultdict(set)

    
    def add_url_connection(self, url: str, outgoing_url: str) -> None:
        if not self.base_url: self.base_url = url
        self.links[url].add(outgoing_url)
    
    def add_asset_connection(self, url: str, asset_link: str) -> None:
        if not self.base_url: self.base_url = url
        self.assets[url].add(asset_link)

    def print_sitemap(self, indent=2) -> None:
        if not self.base_url:
            raise Exception('Cannot print the SiteMap as it does not have a base url!')
        
        curr_indent = 0
        next_level_size = 0
        q = deque([self.base_url])
        curr_level_size = 1
        seen = set()
        while q:
            curr_url = q.popleft()
            if curr_url in seen: continue
            seen.add(curr_url)
            curr_level_size -= 1

            print(('-' * curr_indent) + curr_url)
            print(('-' * curr_indent) + 'Assets:')
            for asset_url in self.assets[curr_url]:
                print(((curr_indent + indent) * '-') + asset_url)

            print(('-' * curr_indent)  + 'Outgoing Urls:')
            for outgoing_url in self.links[curr_url]:
                print(((curr_indent + indent) * '-') + outgoing_url)
                next_level_size += 1

            if curr_level_size == 0:
                curr_indent += indent
                curr_indent = next_level_size
                next_level_size = 0


