# -*- coding: utf-8 -*-

import json
import base64
from botocore.exceptions import ClientError


class InMemoryCache:
    def __init__(self):
        self._dict = {}

    def put(self, id, item):
        self._dict[id] = item

    def get(self, id):
        return self._dict.get(id)

class S3Cache:
    def __init__(self, s3bucket, prefix = '', use_encoded_object_key = False):
        self._bucket = s3bucket
        self._prefix = prefix
        self._use_encoded_object_key = use_encoded_object_key

    def _generate_object_key(self, id):
        object_key = base64.b64encode(id.encode('utf-8')).decode() if self._use_encoded_object_key else id
        return self._prefix + object_key

    def get_dict(self, id, logger = None):
        res = self.get(id, logger)
        return json.loads(res) if res else None

    def get(self, id, logger = None):
        try:
            res = self._bucket.Object(self._generate_object_key(id)).get()
            return res['Body'].read().decode('utf-8')
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if not error_code == 'NoSuchKey' and logger is not None:
                logger.error("Unexpected error: %s" % error_code)
            return None

    def put_dict(self, id, dict, logger = None):
        data = bytearray(json.dumps(dict, ensure_ascii = False).encode())
        self.put(id, data)

    def put(self, id, bin_data, logger = None):
        try:
            res = self._bucket.Object(self._generate_object_key(id)).put(Body = bin_data)
            if logger is not None:
                logger.debug(res)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if logger is not None:
                logger.error("Unexpected error: %s" % error_code)
