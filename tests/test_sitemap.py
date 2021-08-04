from unittest.mock import patch

import pytest
import random
import string

from sitemap import SiteMapManager


def random_url(base_url: str = 'http://test.com') -> str:
    return base_url + '/' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


@pytest.fixture
def sitemap_manager():
    return SiteMapManager(base_url='http://test.com')


def test_add_url_connection(sitemap_manager):
    outgoing_link = random_url(base_url=sitemap_manager.base_url)
    sitemap_manager.add_url_connection(sitemap_manager.base_url, outgoing_link)
    outgoing_links = sitemap_manager.get_outgoing_links(sitemap_manager.base_url)
    assert len(outgoing_links) == 1
    assert outgoing_link in outgoing_links


def test_add_dead_link(sitemap_manager):
    dead_link = random_url()
    sitemap_manager.add_dead_link(dead_link)
    dead_links = sitemap_manager.get_dead_links()
    assert len(dead_links) == 1
    assert dead_link in dead_links


def test_add_asset_connection(sitemap_manager):
    base_url = 'http://test.com'
    asset_link = random_url(base_url=base_url)
    sitemap_manager.add_asset_connection(base_url, asset_link)
    asset_links = sitemap_manager.get_assets(base_url)
    assert len(asset_links) == 1
    assert asset_link in asset_links


@patch('builtins.print')
def test_print_sitemap(mocked_print, sitemap_manager):
    levels = [[sitemap_manager.get_base_url()]]
    for i in range(random.randint(2, 4)):
        level = []
        for j in range(random.randint(2, 4)):
            level.append(random_url())
        levels.append(level)

    for i in range(len(levels) - 1, 0, -1):
        for j in range(len(levels[i])):
            sitemap_manager.add_url_connection(
                levels[i - 1][random.randint(0, len(levels[i - 1]) - 1)],
                levels[i][j]
            )

    indent = random.randint(2, 4)
    sitemap_manager.print_sitemap(indent=indent)
    import pdb;
    pdb.set_trace()
    for level_num, level in enumerate(levels):
        for link in level:
            mocked_print.assert_called_with(((level_num * indent) * '-') + link)
