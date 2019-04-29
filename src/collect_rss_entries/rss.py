# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Optional, List


class RSSConfig:
    def __init__(self, items: List[RSSConfigItem], fmt: str):
        self._items = items
        self._format = fmt

    @staticmethod
    def of(dic) -> Optional[RSSConfig]:
        try:
            items = [RSSConfigItem.of(i) for i in dic['items']]
            fmt = dic.get('format')
            return RSSConfig(items, fmt)
        except KeyError:
            return None

    def get_items(self) -> List[RSSConfigItem]:
        return self._items

    def get_format(self) -> str:
        return self._format


class RSSConfigItem:
    def __init__(self, url: str, id_prefix: str):
        self._url = url
        self._id_prefix = id_prefix

    @staticmethod
    def of(dic) -> Optional[RSSConfigItem]:
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
