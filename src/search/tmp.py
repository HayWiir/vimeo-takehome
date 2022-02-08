#!/usr/bin/env python3
#-*- coding: utf-8 -*-


from traceback import format_exception_only
from elasticsearch import Elasticsearch

elastic_client = Elasticsearch(hosts=["localhost"])

q = "Tennis"

some_query = {"match": { "contents": { "query": q, "lenient":"true"} }}

query_filter = {"bool": { 
      "must": [
        { "match": { "contents": { "query": q, "lenient":"true",} }},
      ],
      "filter": [ 
        { "match":  { "list": "Athletes" }},
      ]
    }}

# query_2 = {"multi_match" : {"query" : q, "fields": ["contents", "title"]}}

result = elastic_client.search(index="wikis", query=some_query, size=10000, filter_path=['hits.hits._source'])

# print(result['hits']['hits'][0]["_source"]["title"])

print(result['hits']['hits'][0].keys())

for i in result['hits']['hits']:
    # print("%s\t\t%s\t%s" % (i["_source"]["title"], i["_source"]["link"], i["_source"]["list"]))
    print(i["_source"]["title"], ":", i["_source"]["list"], "\n" )

print(len(result['hits']['hits']))