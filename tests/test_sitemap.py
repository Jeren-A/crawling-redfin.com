from unittest.mock import patch

import pytest
import random
import string

from sitemap import SiteMapManager


def random_url(base_url: str = None) -> str:
    if not base_url:
        base_url = 'http://test.com'
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
def test_print_sitemap(sitemap_manager):
    # TODO: Build a sitemap level by level then call assert_called_with on print to make sure
    # the links/assets are getting printed in the correct order
    pass