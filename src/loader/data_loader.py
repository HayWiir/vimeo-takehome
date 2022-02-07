import logging
import os
from functools import lru_cache

import elasticsearch
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

ES_HOST = os.environ.get('ES_HOST', 'elasticsearch:9200')
INDEX_NAME = 'wikis'
URL = 'https://en.wikipedia.org/wiki/Wikipedia:Multiyear_ranking_of_most_viewed_pages'
WIKI_API = 'https://en.wikipedia.org/w/api.php'
REPO_NAME = 'wikisrepo'
SNAPSHOT_NAME = 'wikis'
SNAPSHOT_DIR = os.environ.get('SNAPSHOT_DIR', '/snapshot')

LIST_INDEX_TO_NAME = {
    0: 'Top-100 list',
    1: 'Countries',
    2: 'Cities',
    3: 'Buildings & Structures & Statues',
    4: 'People',
    5: 'Singers',
    6: 'Actors',
    7: 'Romantic Actors',
    8: 'Athletes',
    9: 'Modern Political Leaders',
    10: 'Pre-modern people',
    11: '3rd-millennium people'
}

INDEX_BODY = {
    "settings": {
      "index": {
        "number_of_shards": 8,
        "number_of_replicas": 1
        }
    },
    "mappings": {
      "_meta": {
        "index_type": "wikis",
        "version": "1.0",
      },
      "_source": {
        "enabled": True
      },
      "properties": {
        "link": {
          "type": "keyword"
        },
        "title": {
          "type": "text",
        },
        "contents": {
          "type": "text"
        },
        "list": {
            "type": "text"
        },
        "rank": {
            "type": "integer"
        }
      }
    }
}


@lru_cache()
def _client_for_host(host):
    return elasticsearch.Elasticsearch(host)


def create_repo():
    _client_for_host(ES_HOST).snapshot.create_repository(repository=REPO_NAME, body={'type': 'fs', 'settings':
        {'location': '/snapshot'}})


def prep_index():
    snapshot_contents = [f for f in os.listdir(SNAPSHOT_DIR) if f != '.gitignore']
    if snapshot_contents:
        logger.info('Restoring wikis index')
        create_repo()
        try:
            _client_for_host(ES_HOST).snapshot.restore(repository=REPO_NAME, snapshot=SNAPSHOT_NAME)
        except elasticsearch.exceptions.TransportError as e:
            if 'an open index with same name already exists' in str(e):
                logger.info('Index already exists, nothing to do')
            else:
                raise e
    else:
        logger.error("Couldn't find snapshot to restore")
    logger.info('Done')


if __name__ == '__main__':
    prep_index()
