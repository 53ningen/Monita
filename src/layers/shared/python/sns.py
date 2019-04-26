# -*- coding: utf-8 -*-

import json

def notify(snscli, item, topic, logger):
    j = json.dumps(item, ensure_ascii=False)
    logger.debug(j)
    res = snscli.publish(
        TopicArn=topic,
        Message=j,
    )
    logger.info(res)
    return res
