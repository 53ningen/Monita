# -*- coding: utf-8 -*-

import os
import boto3
import feedparser

import rss
import log
import cache
import config
import sns

logger = None

config_key_name = os.environ['ConfigKeyName']
monita_bucket = os.environ['MonitaBucket']
topic = os.environ['TopicArn']

in_memory_cache = cache.InMemoryCache()
s3_cache = cache.S3Cache(boto3.resource('s3').Bucket(monita_bucket), 'data/rss/', True)

snscli = boto3.client('sns')
config_bucket = boto3.resource('s3').Bucket(os.environ['ConfigBucket'])


def handle_entries(entries, rss_config_item, topic) -> int:
    new_entry = 0
    for entry in entries:
        try:
            id = rss_config_item.generate_id(entry.id)
            if in_memory_cache.get(id):
                continue
            if s3_cache.get(id):
                in_memory_cache.put(id, entry)
                continue
            sns.notify(snscli, entry, topic, logger)
            in_memory_cache.put(id, entry)
            s3_cache.put_dict(id, entry)
            new_entry += 1
        except Exception as e:
            logger.error(e)
            continue
    return new_entry

def lambda_handler(event, context):
    dict = config.load_config_file(config_bucket, config_key_name)
    rss_config = rss.RSSConfig.of(dict['functions']['collect_rss_entries'])
    global logger
    logger = log.get_logger(dict['globals']['log_level'])

    new_entry = 0
    for rss_config_item in rss_config.get_items():
        try:
            res = feedparser.parse(rss_config_item.get_url())
            new_entry += handle_entries(res.entries, rss_config_item, topic)
        except Exception as e:
            logger.error(e)
            continue
    return {
        'new_entry': new_entry
    }
