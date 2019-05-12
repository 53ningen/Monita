Monita
======

Serverless App for Monitoring Website Changes


# What is Monita?
## Detect Website Changes

When the content of webpage written in config file updated, this app send a message to the configured SNS topic.

If you create email subscription in the target SNS topic, you can receive the notification of website changes.


The configuration file: config.template.yaml is as follows:

```yaml
---

globals:
  log_level: INFO
functions:
  detect_website_changes:
    items:
      -
        url: http://example.com
        selector: 'body'
```

The message notified to the configured SNS topic is as follows:

```json
{
  "id": "example.com",
  "title": "Example Domain",
  "title_detail": {
    "type": "text/plain",
    "language": "ja",
    "base": "http://example.com",
    "value": "Example Domain"
  },
  "links": [
    {
      "rel": "alternate",
      "type": "text/html",
      "href": "http://example.com"
    }
  ],
  "link": "http://example.com",
  "hash": "7c0dad7c0a2ae27bb379a3670edc5f67",
  "summary": "\n\nExample Domain\nThis domain is established to be used for illustrative examples in documents. You may use this\n    domain in examples without prior coordination or asking for permission.\nMore information...\n\n",
  "summary_detail": {
    "type": "text/html",
    "language": "ja",
    "base": "http://example.com",
    "value": "\n\nExample Domain\nThis domain is established to be used for illustrative examples in documents. You may use this\n    domain in examples without prior coordination or asking for permission.\nMore information...\n\n"
  },
  "updated": "2019-04-26T18:40:05+00:00",
  "updated_parsed": [
    2019,
    4,
    26,
    18,
    40,
    5,
    4,
    116,
    -1
  ]
}
```


## Detect New Entry of RSS Feed

When the new entry of RSS feed posted, this app send a message to the configured SNS topic.

The configuration file: config.template.yaml is as follows:

```yaml
---

globals:
  log_level: INFO
functions:
  collect_rss_entries:
    items:
      -
        url: https://ameblo.jp/wakeupgirls/rss.html
        id_prefix: wug
```


# Configuration

1. `cp ./config.template.yaml config.dev.yaml`. (or `config.prod.yaml`)
2. Update `config.dev.yaml`

```yaml
---

globals:
  log_level: DEBUG  # LOG_LEVEL: [DEBUG|INFO|WRAN|ERROR]
functions:
  collect_rss_entries:
    items:
      -
        url: https://ameblo.jp/rungirlsrun/rss.html # [required] RSS Feed you want to detect new entry
        id_prefix: rgr                              # [option] used for the id prefix of messages sent to SNS topic
  detect_website_changes:
    items:
      -
        url: http://example.com     # [required] Website URL you want to detect changes
        selector: 'body'            # [required] CSS selector you want to detect changes
        title: example page         # [option] used for the title of messages sent to SNS topic
```


# Deployment

1. `cp ./.env.template .env.dev`. (or `.env.prod`)
2. Update `.env.dev`
3. `./script/update_config dev`
4. `./script/deploy dev`


# Resources

This app will create following resources:

- Lambda Functions
- CloudWatch Logs, Log Group
- S3 Bucket


# Run locally

Prepare:

```
$ docker-compose up -d
$ awslocal s3api create-bucket --bucket monita-config
$ awslocal s3api create-bucket --bucket monita-cache
$ awslocal s3 cp ./config.dev.yaml s3://monita-config/config.yaml
```

Invoke locally:

```
$ awslocal sns create-topic --name test --region ap-northeast-1
$ sam local invoke DetectWebsiteChangesFunction --no-event \
    --env-vars local-vars.json \
    --docker-network `docker network ls | grep monita_default | awk '{print $1}'`
```