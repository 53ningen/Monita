# -*- coding: utf-8 -*-

import json

def notify(snscli, message, topic, logger):
    logger.debug(message)
    res = snscli.publish(
        TopicArn=topic,
        Message=message,
    )
    logger.info(res)
    return res
