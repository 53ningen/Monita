# -*- coding: utf-8 -*-

from urllib.parse import urlparse

class WebsiteConfig:
    def __init__(self, items):
        self._items = items

    @staticmethod
    def of(dict):
        try:
            items = [WebsiteConfigItem.of(i) for i in dict['items']]
            return WebsiteConfig(items)
        except KeyError:
            return None

    def get_items(self):
        return self._items


class WebsiteConfigItem:
    def __init__(self, url, selector, id_prefix, title):
        self._url = url
        self._selector = selector
        self._id_prefix = id_prefix
        self._title = title

    @staticmethod
    def of(dict):
        try:
            url = dict['url']
            selector = dict.get('selector')
            id_prefix = dict.get('id_prefix') or ''
            title = dict.get('title') or None
            return WebsiteConfigItem(url, selector, id_prefix, title)
        except KeyError:
            return None

    def get_url(self) -> str:
        return self._url

    def get_selector(self) -> str:
        return self._selector

    def get_object_key(self) -> str:
        res = urlparse(self._url)
        return res.netloc + res.path + res.query

    def get_title(self) -> str:
        return self._title
