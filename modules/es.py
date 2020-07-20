from elasticsearch import Elasticsearch
from elasticsearch import helpers
from my_parser import Parser
import json


class ES:

    def __init__(self):
        self.stop_list = self.read_stop()
        self.template = {
                            "index_patterns": "hw3",
                            "settings": {
                                "number_of_replicas": 1,
                                "index.highlight.max_analyzed_offset": 2000000,
                                "analysis": {
                                    "filter": {
                                        "english_stop": {
                                            "type": "stop",
                                            "stopwords": self.stop_list,
                                        },
                                        "my_snow": {
                                            "type": "snowball",
                                            "language": "English"
                                        }
                                    },
                                    "analyzer": {
                                        # custom analyzer "stopped"
                                        "stopped_stem": {
                                            "type": "custom",
                                            "tokenizer": "standard",
                                            "filter": [
                                                "lowercase",
                                                # custom filter "english_stop"
                                                "english_stop",
                                                "my_snow"
                                            ]
                                        }
                                    }
                                }
                            },
                            "mappings": {
                                "_source": {
                                    "enabled": "true"
                                },
                                "properties": {
                                    # fields
                                    "http_header": {
                                        "type": "keyword"
                                    },
                                    "title": {
                                      "type": "keyword"
                                    },
                                    "text_content": {
                                        "type": "text",
                                        "fielddata": "true",
                                        "analyzer": "stopped_stem",
                                        "index_options": "positions",
                                    },
                                    "raw_html": {
                                        "type": "text",
                                        "index": "false"
                                    },
                                    "in_links": {
                                        "type": "keyword"
                                    },
                                    "out_links": {
                                        "type": "keyword"
                                    }
                                }
                            }
                        }
        self.hosts = ["https://f2ff43d409574698a747eaa43256d1e0.northamerica-northeast1.gcp.elastic-cloud.com:9243/"]
        self.cloud_id = "CS6200:bm9ydGhhbWVyaWNhLW5vcnRoZWFzdDEuZ2NwLmVsYXN0aWMtY2xvdWQuY29tJGYyZmY0M2Q0MDk1NzQ2OThhNzQ3ZWFhNDMyNTZkMWUwJDU1ZTY4MGVhZjQ5MjRmNmM5NmY5YmIxNTRjZTQyN2Fk"
        self.name = "web_crawler"
        self.index = "hw3"
        self.es = Elasticsearch(hosts=self.hosts, timeout=60, clould_id=self.cloud_id, http_auth=('elastic', 'nRGUXlzD1f8kOT63iLehSG9a'))
        self.parser = Parser()

    def initialize(self):
        self.read_stop()
        # self.es.indices.delete(index=self.index)
        self.es.indices.put_template(name=self.name, body=self.template)
        self.es.indices.create(index=self.index)

    def es_control(self):
        self.parser.initialize("./output/")
        # upload docs, headers
        docs, headers = self.parser.doc_parse()
        actions = [
            {
                "_op_type": "update",
                "_index": self.index,
                "_id": id,
                "doc": {
                    "http_header": str(headers[id]),
                    "title": "",
                    "text_content": docs[id],
                    "raw_html": "",
                    "in_links": "",
                    "out_links": ""
                },
                "doc_as_upsert": "true"
            }
            for id in docs
        ]
        helpers.bulk(self.es, actions=actions)
        docs, headers = None, None

        # upload title
        titles = self.parser.title_parse()
        actions = [
            {
                "_op_type": "update",
                "_index": self.index,
                "_id": id,
                "script": {
                    "source": """
                                if (ctx._source["title"] == "") {
                                    ctx._source["title"] = params["title"]
                                }
                            """,
                    "lang": "painless",
                    "params": {
                        "title": titles[id]
                    }
                }
            }
            for id in titles
        ]
        helpers.bulk(self.es, actions=actions)
        titles = None

        # upload html
        for i in range(20):
            raw_html = self.parser.html_parse(2000*i, 2000*(i+1))
            actions = [
                {
                    "_op_type": "update",
                    "_index": self.index,
                    "_id": id,
                    "script": {
                        "source": """
                            if (ctx._source["raw_html"] == "") {
                                ctx._source["raw_html"] = params["html"]
                            }
                        """,
                        "lang": "painless",
                        "params": {
                            "html": raw_html[id]
                        }
                    }
                }
                for id in raw_html
            ]
            helpers.bulk(self.es, actions=actions)
            raw_html = None

        # upload in_links, out_links
        in_links, out_links = self.parser.links_parse()
        # with open("./output/test_in_links.json", "r") as f:
        #     in_links = json.load(f)
        # with open("./output/test_out_links.json", "r") as f:
        #     out_links = json.load(f)
        actions = [
            {
                "_op_type": "update",
                "_index": self.index,
                "_id": id,
                "script": {
                    "source": """
                                if (ctx._source["in_links"] == "") {
                                    ctx._source["in_links"] = params["in_links"]
                                } else {
                                    for (int i = 0; i < params["length"]; ++i) {
                                        if (ctx._source["in_links"].contains(params["in_links"][i]) == false) {
                                            ctx._source["in_links"].add(params["in_links"][i])
                                        }
                                    }
                                }
                            """,
                    "lang": "painless",
                    "params": {
                        "in_links": in_links[id],
                        "length": len(in_links[id])
                    }
                }
            }
            for id in in_links
        ]
        helpers.bulk(self.es, actions=actions)

        actions = [
            {
                "_op_type": "update",
                "_index": self.index,
                "_id": id,
                "script": {
                    "source": """
                        if (ctx._source["out_links"] == "") {
                            ctx._source["out_links"] = params["out_links"]
                        } else {
                            for (int i = 0; i < params["length"]; ++i) {
                                if (ctx._source["out_links"].contains(params["out_links"][i]) == false) {
                                    ctx._source["out_links"].add(params["out_links"][i])
                                }
                            }
                        }
                    """,
                    "lang": "painless",
                    "params": {
                        "out_links": out_links[id],
                        "length": len(out_links[id])
                    }
                }
            }
            for id in out_links
        ]
        helpers.bulk(self.es, actions=actions)

    def read_stop(self):
        stop_list = []
        with open("E:/Will/work/NEU/CS 6200/Python Project/stoplist.txt", "r") as f:
            for line in f.readlines():
                stop_list.append(line.replace("\n", ""))
        return stop_list

# test = ES()
# index_name = "test"
# cloud_id = "ZC_CS6200:bm9ydGhhbWVyaWNhLW5vcnRoZWFzdDEuZ2NwLmVsYXN0aWMtY2xvdWQuY29tJGU2NzdlY2JlYzM4ZjRjYTZhOTNhNjUzOGQ2ZGMyOTE4JGUyYmZiMjAwNjY2NjRlOTVhNjc0ZWY0OWE5ODBhMzkz"
# es = Elasticsearch(hosts=["https://e677ecbec38f4ca6a93a6538d6dc2918.northamerica-northeast1.gcp.elastic-cloud.com:9243/"], clould_id=cloud_id, http_auth=('elastic', 'rlj3NbyVqLOIUKKHhH4OGAjC'))
# es.indices.delete("")
# es.search(index="hw3",
#           body={
#               "query": {"match": {"text_content": "ten"}}
#           })
# doc = {
#     'author': 'kimchy',
#     'text': 'Elasticsearch: cool. bonsai cool.'
# }
# es.index(index="test", id = 1, body=doc)
