# -*- coding: utf-8 -*-

class RSSConfig:
    def __init__(self, items):
        self._items = items

    @staticmethod
    def of(dict):
        try:
            items = [RSSConfigItem.of(i) for i in dict['items']]
            return RSSConfig(items)
        except KeyError:
            return None

    def get_items(self):
        return self._items


class RSSConfigItem:
    def __init__(self, url, id_prefix):
        self._url = url
        self._id_prefix = id_prefix

    @staticmethod
    def of(dict):
        try:
            url = dict['url']
            id_prefix = dict.get('id_prefix') or ''
            return RSSConfigItem(url, id_prefix)
        except KeyError:
            return None

    def get_url(self) -> str:
        return self._url

    def generate_id(self, original_id) -> str:
        return self._id_prefix + original_id
