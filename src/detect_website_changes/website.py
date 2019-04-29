# -*- coding: utf-8 -*-

from urllib.parse import urlparse


class WebsiteConfig:
    def __init__(self, items, fmt):
        self._items = items
        self._format = fmt

    @staticmethod
    def of(dic):
        try:
            items = [WebsiteConfigItem.of(i) for i in dic['items']]
            fmt = dic['format']
            return WebsiteConfig(items, fmt)
        except KeyError:
            return None

    def get_items(self):
        return self._items

    def get_format(self):
        return self._format


class WebsiteConfigItem:
    def __init__(self, url, selector, id_prefix, title):
        self._url = url
        self._selector = selector
        self._id_prefix = id_prefix
        self._title = title

    @staticmethod
    def of(dic):
        try:
            url = dic['url']
            selector = dic.get('selector')
            id_prefix = dic.get('id_prefix') or ''
            title = dic.get('title') or None
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
