# -*- coding: utf-8 -*-

import yaml
import datetime


def load_config_file(config_bucket, config_key_name):
    timestamp = datetime.datetime.utcnow().timestamp()
    config_path = '/tmp/config.' + str(timestamp)
    config_bucket.download_file(config_key_name, config_path)
    f = open(config_path, "r")
    dic = yaml.load(f, Loader=yaml.SafeLoader)
    f.close()
    return dic
