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
    base_url = sitemap_manager.get_base_url()
    outgoing_link = random_url(base_url=base_url)
    sitemap_manager.add_url_connection(base_url, outgoing_link)
    outgoing_links = sitemap_manager.get_outgoing_links(base_url)
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
    # Generate random tree
    levels = [[sitemap_manager.get_base_url()]]
    assets = [[random_url()]]
    # Create the links and assets by level order
    for i in range(random.randint(1, 10)):
        level = []
        asset_level = []
        for j in range(random.randint(1, 10)):
            level.append(random_url())
        for j in range(random.randint(1, 10)):
            asset_level.append(random_url())
        levels.append(level)
        assets.append(asset_level)

    # Create random connections between links
    for i in range(len(levels) - 1, 0, -1):
        for j in range(len(levels[i])):
            sitemap_manager.add_url_connection(
                levels[i - 1][random.randint(0, len(levels[i - 1]) - 1)],
                levels[i][j]
            )
    # Create random connections between assets and links
    for i in range(len(assets)):
        for j in range(len(assets[i])):
            sitemap_manager.add_asset_connection(
                levels[i][random.randint(0, len(levels[i]) - 1)],
                assets[i][j]
            )

    indent = random.randint(2, 4)
    sitemap_manager.print_sitemap(indent=indent)
    # Make sure that each link is printed with proper indent
    for level_num, level in enumerate(levels):
        for link in level:
            mocked_print.assert_any_call(((level_num * indent) * '-') + link)

    # Make sure that each asset is printed with proper indent
    for level_num, level in enumerate(assets, 1):
        for asset_link in level:
            mocked_print.assert_any_call(((level_num * indent) * '-') + asset_link)
