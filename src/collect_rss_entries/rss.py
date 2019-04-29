# -*- coding: utf-8 -*-


class RSSConfig:
    def __init__(self, items, fmt):
        self._items = items
        self._format = fmt

    @staticmethod
    def of(dic):
        try:
            items = [RSSConfigItem.of(i) for i in dic['items']]
            fmt = dic.get('format')
            return RSSConfig(items, fmt)
        except KeyError:
            return None

    def get_items(self):
        return self._items

    def get_format(self):
        return self._format


class RSSConfigItem:
    def __init__(self, url, id_prefix):
        self._url = url
        self._id_prefix = id_prefix

    @staticmethod
    def of(dic):
        try:
            url = dic['url']
            id_prefix = dic.get('id_prefix') or ''
            return RSSConfigItem(url, id_prefix)
        except KeyError:
            return None

    def get_url(self) -> str:
        return self._url

    def generate_id(self, original_id) -> str:
        return self._id_prefix + original_id
