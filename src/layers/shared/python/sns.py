# -*- coding: utf-8 -*-


def notify(sns_cli, message: str, topic: str, logger):
    logger.debug(message)
    res = sns_cli.publish(
        TopicArn=topic,
        Message=message,
    )
    logger.info(res)
    return res
