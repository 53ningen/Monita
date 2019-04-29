# -*- coding: utf-8 -*-

import os
import json
import boto3
import string
import datetime
import traceback
import hashlib
import requests
from bs4 import BeautifulSoup, Comment

import website
import log
import config
import cache
import sns

logger = None

config_key_name = os.environ['ConfigKeyName']
monita_bucket = os.environ['MonitaBucket']
topic = os.environ['TopicArn']

in_memory_cache = cache.InMemoryCache()
s3_cache = cache.S3Cache(boto3.resource('s3').Bucket(monita_bucket), 'data/website/')

sns_cli = boto3.client('sns')
config_bucket = boto3.resource('s3').Bucket(os.environ['ConfigBucket'])


def create_message(fmt, object_key, url, hash, title, text, time) -> str:
    template = string.Template(fmt)
    return template.substitute({
        'object_key': object_key,
        'url': url,
        'hash': hash,
        'title': title,
        'text': repr(text),
        'iso8601time': time.isoformat(),
        'timetuple': list(time.timetuple())
    })


def create_cache_obj(object_key, hash, message) -> dict:
    return {
      'object_key': object_key,
      'hash': hash,
      'message': message
    }


def check_if_website_updated(item, fmt) -> bool:
    res = requests.get(item.get_url())
    logger.debug(json.dumps({'url':item.get_url(), 'status_code': res.status_code}))
    if res.status_code < 200 or res.status_code >= 300:
        logger.error('Error: ' + item.get_url())
        return False
    soup = BeautifulSoup(res.text, "html.parser")
    [s.decompose() for s in soup('style')]
    [s.decompose() for s in soup('script')]
    [s.decompose() for s in soup if isinstance(s, Comment)]
    title = item.get_title() or soup.select_one('title').text
    selected = soup.select_one(item.get_selector())
    if not selected:
        logger.error('Error: soup.select(...) is None')

    object_key = item.get_object_key()
    hash = hashlib.md5(selected.text.encode()).hexdigest()
    now = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc,microsecond=0)

    message = create_message(fmt, object_key, item.get_url(), hash, title, selected.text, now)
    logger.debug(message)
    cache_obj = create_cache_obj(object_key, hash, message)

    cache = in_memory_cache.get(object_key)
    if cache and cache.get('hash') == hash:
        logger.debug('local cache hit for: ' + item.get_url())
        return False
    cache = s3_cache.get_dict(object_key, logger)
    if cache and cache.get('hash') == hash:
        logger.debug('remote cache hit for: ' + item.get_url())
        in_memory_cache.put(object_key, cache_obj)
        return False
    sns.notify(sns_cli, message, topic, logger)
    in_memory_cache.put(object_key, cache_obj)
    s3_cache.put_dict(object_key, cache_obj, logger)
    return True


def lambda_handler(event, context):
    dic = config.load_config_file(config_bucket, config_key_name)
    website_config = website.WebsiteConfig.of(dic['functions']['detect_website_changes'])
    global logger
    logger = log.get_logger(dic['globals']['log_level'])

    changed = 0
    error = 0
    for item in website_config.get_items():
        try:
            website_changed = check_if_website_updated(item, website_config.get_format())
            if website_changed: changed += 1
        except:
            print(traceback.format_exc())
            error += 1
    return {
        'changed': changed,
        'error': error
    }
