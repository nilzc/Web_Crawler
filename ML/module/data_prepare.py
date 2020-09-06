import pandas as pd


class QREL:
    
    def __init__(self):
        self.qrel_docs = {}
        self.read_qrel()

        self.query_doc = {}
        self.df = pd.DataFrame()

        self.es_score = {}
        self.bm_score = {}
        self.otf_score = {}
        self.tfidf_score = {}
        self.lml_score = {}
        self.lmjm_score = {}

        self.es_score_file()
        self.bm_score_file()
        self.otf_score_file()
        self.tfidf_score_file()
        self.lml_score_file()
        self.lmjm_score_file()
        self.get_final_query_doc()
        self.get_data_frame()

    def read_qrel(self):
        with open("./qrels.adhoc.51-100.AP89.txt", "r") as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                query_id, temp, doc_id, rel = line.split(" ")
                if query_id in self.qrel_docs:
                    self.qrel_docs[query_id][doc_id] = rel
                else:
                    self.qrel_docs[query_id] = {}
                    self.qrel_docs[query_id][doc_id] = rel

    def es_score_file(self):
        with open("./scores/ES_hw6.txt", "r") as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                query_id, temp, doc_id, rank, score, exp = line.split(" ")
                if query_id in self.es_score:
                    self.es_score[query_id][doc_id] = score
                else:
                    self.es_score[query_id] = {}
                    self.es_score[query_id][doc_id] = score

    def bm_score_file(self):
        with open("./scores/BM_hw6.txt", "r") as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                query_id, temp, doc_id, rank, score, exp = line.split(" ")
                if query_id in self.bm_score:
                    self.bm_score[query_id][doc_id] = score
                else:
                    self.bm_score[query_id] = {}
                    self.bm_score[query_id][doc_id] = score

    def otf_score_file(self):
        with open("./scores/OTF_hw6.txt", "r") as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                query_id, temp, doc_id, rank, score, exp = line.split(" ")
                if query_id in self.otf_score:
                    self.otf_score[query_id][doc_id] = score
                else:
                    self.otf_score[query_id] = {}
                    self.otf_score[query_id][doc_id] = score

    def tfidf_score_file(self):
        with open("./scores/TFIDF_hw6.txt", "r") as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                query_id, temp, doc_id, rank, score, exp = line.split(" ")
                if query_id in self.tfidf_score:
                    self.tfidf_score[query_id][doc_id] = score
                else:
                    self.tfidf_score[query_id] = {}
                    self.tfidf_score[query_id][doc_id] = score

    def lml_score_file(self):
        with open("./scores/LML_hw6.txt", "r") as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                query_id, temp, doc_id, rank, score, exp = line.split(" ")
                if query_id in self.lml_score:
                    self.lml_score[query_id][doc_id] = score
                else:
                    self.lml_score[query_id] = {}
                    self.lml_score[query_id][doc_id] = score

    def lmjm_score_file(self):
        with open("./scores/LMJM_0.9_hw6.txt", "r") as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                query_id, temp, doc_id, rank, score, exp = line.split(" ")
                if query_id in self.lmjm_score:
                    self.lmjm_score[query_id][doc_id] = score
                else:
                    self.lmjm_score[query_id] = {}
                    self.lmjm_score[query_id][doc_id] = score

    def get_final_query_doc(self):
        for i in self.es_score:
            self.query_doc[i] = set()
            for doc in self.qrel_docs[i]:
                self.query_doc[i].add(doc)
            for doc in self.es_score[i]:
                self.query_doc[i].add(doc)
                
    def get_data_frame(self):
        queries = []
        docs = []
        es = []
        otf = []
        bm = []
        tfidf = []
        lml = []
        lmjm = []
        rel = []
        for q in self.query_doc:
            for doc in self.query_doc[q]:
                queries.append(q)
                docs.append(doc)
                es.append(self.es_score[q][doc])
                otf.append(self.otf_score[q][doc])
                bm.append(self.bm_score[q][doc])
                tfidf.append(self.tfidf_score[q][doc])
                lml.append(self.lml_score[q][doc])
                lmjm.append(self.lmjm_score[q][doc])
                if doc in self.qrel_docs[q]:
                    rel.append(self.qrel_docs[q][doc])
                else:
                    rel.append(0)
        self.df = pd.DataFrame({"query": queries,
                                "doc": docs,
                                "es": es,
                                "otf": otf,
                                "bm": bm,
                                "tfidf": tfidf,
                                "lml": lml,
                                "lmjm": lmjm,
                                "label": rel})
