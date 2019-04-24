# -*- coding: utf-8 -*-

import os
import json
import yaml
import boto3
import datetime

import website
import log
import cache
import hashlib
import requests
from bs4 import BeautifulSoup

logger = None

config_key_name = os.environ['ConfigKeyName']
monita_bucket = os.environ['MonitaBucket']
topic = os.environ['TopicArn']

in_memory_cache = cache.InMemoryCache()
s3_cache = cache.S3Cache(boto3.resource('s3').Bucket(monita_bucket), 'data/website/')

sns = boto3.client('sns')
config_bucket = boto3.resource('s3').Bucket(os.environ['ConfigBucket'])

def notify(item, topic):
    j = json.dumps(item, ensure_ascii=False)
    logger.debug(j)
    res = sns.publish(
        TopicArn=topic,
        Message=j,
    )
    logger.info(res)
    return res

def load_config_file():
    timestamp = datetime.datetime.utcnow().timestamp()
    config_path = '/tmp/config.' + str(datetime.datetime.utcnow().timestamp())
    config_bucket.download_file(config_key_name, config_path)
    f = open(config_path, "r")
    dict = yaml.load(f, Loader=yaml.SafeLoader)
    f.close()
    return dict

def check_if_website_updated(item) -> bool:
    res = requests.get(item.get_url())
    logger.debug(json.dumps({'url':item.get_url(), 'status_code': res.status_code}))
    if res.status_code < 200 or res.status_code >= 300:
        logger.error('Error: ' + item.get_url())
        return False
    soup = BeautifulSoup(res.text, "html.parser")
    selected = soup.select_one('#contents')
    if not selected:
        logger.error('Error: soup.select(...) is None')

    hash = hashlib.md5(selected.text.encode()).hexdigest()
    obj = {
        'id': item.get_object_key(),
        'url': item.get_url(),
        'selector': item.get_selector(),
        'hash': hash,
        'text': selected.text
    }

    cache = in_memory_cache.get(item.get_object_key())
    if cache and cache.get('hash') == hash:
        logger.debug('local cache hit for: ' + item.get_url())
        return False
    cache = s3_cache.get_dict(item.get_object_key(), logger)
    if cache and cache.get('hash') == hash:
        logger.debug('remote cache hit for: ' + item.get_url())
        in_memory_cache.put(item.get_object_key(), obj)
        return False
    notify(obj, topic)
    in_memory_cache.put(item.get_object_key(), obj)
    s3_cache.put_dict(item.get_object_key(), obj, logger)
    return True

def lambda_handler(event, context):
    dict = load_config_file()
    website_config = website.WebsiteConfig.of(dict['functions']['detect_website_changes'])
    global logger
    logger = log.get_logger(dict['globals']['log_level'])

    changed = 0
    for item in website_config.get_items():
        website_changed = check_if_website_updated(item)
        if website_changed: changed += 1
    return {
        'changed': changed
    }
