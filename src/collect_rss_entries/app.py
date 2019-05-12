# -*- coding: utf-8 -*-

import os
import json
import boto3
import string
import feedparser

from rss import RSSConfig, RSSConfigItem
import log
import cache
import config
import sns

logger = None

config_key_name = os.environ['ConfigKeyName']
monita_bucket = os.environ['MonitaBucket']
topic = os.environ['TopicArn']

in_memory_cache = cache.InMemoryCache()

session = boto3.session.Session()
if os.environ['Stage'] == 'local':
    sns_cli = session.client('sns', endpoint_url='http://localstack:4575')
    s3_cache = cache.S3Cache(session.resource('s3', endpoint_url='http://localstack:4572').Bucket(monita_bucket), 'data/rss/', True)
    config_bucket = boto3.resource('s3', endpoint_url='http://localstack:4572').Bucket(os.environ['ConfigBucket'])
else:
    sns_cli = session.client('sns')
    s3_cache = cache.S3Cache(session.resource('s3').Bucket(monita_bucket), 'data/rss/', True)
    config_bucket = boto3.resource('s3').Bucket(os.environ['ConfigBucket'])

def create_message(fmt: str, entry) -> str:
    if fmt is None:
        return entry
    else:
        template = string.Template(fmt)
        return template.substitute(dict(entry))


def handle_entries(entries, rss_config_item: RSSConfigItem, topic: str, fmt: str) -> int:
    new_entry = 0
    for entry in entries:
        try:
            id = rss_config_item.generate_id(entry.id)
            if in_memory_cache.get(id):
                continue
            if s3_cache.get(id):
                in_memory_cache.put(id, entry)
                continue
            message = create_message(fmt, entry)
            sns.notify(sns_cli, json.dumps(message, ensure_ascii=False), topic, logger)
            in_memory_cache.put(id, entry)
            s3_cache.put_dict(id, entry)
            new_entry += 1
        except Exception as e:
            logger.error(e)
            continue
    return new_entry


def lambda_handler(event, context):
    dic = config.load_config_file(config_bucket, config_key_name)
    rss_config = RSSConfig.of(dic['functions']['collect_rss_entries'])
    global logger
    logger = log.get_logger(dic['globals']['log_level'])

    new_entry = 0
    for rss_config_item in rss_config.get_items():
        try:
            res = feedparser.parse(rss_config_item.get_url())
            new_entry += handle_entries(res.entries, rss_config_item, topic, rss_config.get_format())
        except Exception as e:
            logger.error(e)
            continue
    return {
        'new_entry': new_entry
    }
