import os
from flask import Flask, jsonify, request
import requests
from elasticsearch import Elasticsearch

elastic_client = Elasticsearch(
    ["http://elasticsearch:9200"], retry_on_timeout=True, request_timeout=30
)
app = Flask(__name__)


@app.route("/status")
def status():
    return jsonify({"status": "green"})


@app.route("/search/wikis", methods=["GET"])
def search():
    args = request.args

    text_query = args.get("q", None)
    list_option = args.get("list", None)

    regular_query = {
        "match": {
            "contents": {"query": text_query, "lenient": "true", "fuzziness": "AUTO"}
        }
    }
    filter_query = {
        "bool": {
            "must": [
                {
                    "match": {
                        "contents": {
                            "query": text_query,
                            "lenient": "true",
                        }
                    }
                },
            ],
            "filter": [
                {"match": {"list": list_option}},
            ],
        }
    }

    search_query = regular_query if list_option is None else filter_query

    result = elastic_client.search(
        index="wikis", query=search_query, size=10000, filter_path=["hits.hits._source"]
    )

    try:
        hits_list = result["hits"]["hits"]

        ret_results = []

        for hit in hits_list:
            ret_results.append(
                {"title": hit["_source"]["title"], "link": hit["_source"]["link"]}
            )

        final = {"number_of_results": len(hits_list), "results": ret_results}

    except KeyError:
        final = {}

    return jsonify(final)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT"))
