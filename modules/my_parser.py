import json
from progressbar import ProgressBar, Bar, Percentage
from canonicalization import Canonicalizer
import re


class Parser:

    def __init__(self):
        self.path = ""
        self.doc = "documents.txt"
        self.raw_html = "raw_html.json"
        self.in_links = "new_in_links.json"
        self.out_links = "new_out_links.json"
        self.count = 40000
        self.canonicalizer = Canonicalizer()

    def initialize(self, path: str):
        self.path = path

    def doc_parse(self):
        # needed objects
        docs = {}
        headers = {}
        doc = list()
        add_file_flag = 0
        txt_flag = 0
        with open(self.path + self.doc, "r", encoding="utf-8") as f:
            bar = ProgressBar(widgets=["Read docs: ", Bar(), Percentage()], maxval=self.count)
            bar.start()
            count = 0
            for line in f:
                line = line.strip()
                # file end
                if re.search("</DOC>", line):
                    add_file_flag = 0
                    docs[data_id] = ' '.join(doc)
                    headers[data_id] = data_header
                    doc = list()
                    count += 1
                    bar.update(count)
                    if count == self.count:
                        bar.finish()
                        return docs, headers
                # add lines to file
                if add_file_flag == 1:
                    # id
                    if re.search("</DOCNO>", line):
                        data_id = re.sub("(<DOCNO>)|(</DOCNO>)", "", line)
                    # header
                    if re.search("</HEADER>", line):
                        data_header = json.loads(re.sub("(<HEADER>)|(</HEADER>)", "", line))
                    # text
                    # text end
                    if re.search("</TEXT>", line):
                        txt_flag = 0
                    if txt_flag == 1:
                        doc.append(line)
                    # text start
                    if re.search("<TEXT>", line):
                        if re.search("[A-Z|a-z]*[a-z]", line):
                            doc.append(line[6:])
                        txt_flag = 1
                # file start
                if re.search("<DOC>", line):
                    add_file_flag = 1
            bar.finish()
        return docs, headers

    def title_parse(self):
        # needed objects
        docs = {}
        doc = list()
        add_file_flag = 0
        txt_flag = 0
        with open(self.path + self.doc, "r", encoding="utf-8") as f:
            bar = ProgressBar(widgets=["Read title: ", Bar(), Percentage()], maxval=self.count)
            bar.start()
            count = 0
            for line in f:
                line = line.strip()
                # file end
                if re.search("</DOC>", line):
                    add_file_flag = 0
                    docs[data_id] = ''.join(doc)
                    doc = list()
                    count += 1
                    bar.update(count)
                    if count == self.count:
                        bar.finish()
                        return docs
                # add lines to file
                if add_file_flag == 1:
                    # id
                    if re.search("</DOCNO>", line):
                        data_id = re.sub("(<DOCNO>)|(</DOCNO>)", "", line)
                    # title
                    # title end
                    if re.search("</HEAD>", line):
                        txt_flag = 0
                    if txt_flag == 1:
                        doc.append(line)
                    # title start
                    if re.search("<HEAD>", line):
                        if re.search("</HEAD>", line):
                            doc.append(re.sub("(<HEAD>)|(</HEAD>)", "", line))
                            txt_flag = 0
                        else:
                            txt_flag = 1
                # file start
                if re.search("<DOC>", line):
                    add_file_flag = 1
            bar.finish()
        return docs

    def html_parse(self, start, end):
        raw_html = {}
        count = 0
        with open(self.path + self.raw_html, "r", encoding="utf-8") as fh:
            bar = ProgressBar(widgets=["Read html: ", Bar(), Percentage()], maxval=end)
            bar.start()
            for line in fh:
                count += 1
                if count > end:
                    bar.finish()
                    return raw_html
                if count >= start:
                    raw_html.update(json.loads(line))
                bar.update(count)
            bar.finish()
        return raw_html

    def links_parse(self):
        in_links = {}
        out_links = {}
        count = 0
        with open(self.path + self.in_links, "r", encoding="utf-8") as fi:
            bar = ProgressBar(widgets=["Read in_links: ", Bar(), Percentage()], maxval=40000)
            bar.start()
            for line in fi:
                in_links.update(json.loads(line))
                count += 1
                bar.update(count)
            bar.finish()
        count = 0
        with open(self.path + self.out_links, "r", encoding="utf-8") as fo:
            bar = ProgressBar(widgets=["Read out_links: ", Bar(), Percentage()], maxval=40000)
            bar.start()
            for line in fo:
                out_links.update(json.loads(line))
                count += 1
                bar.update(count)
            bar.finish()
        with open(self.path + "crawled_links.txt", "a") as f:
            for url in in_links:
                f.write(url)
                f.write("\n")
        return in_links, out_links

    def reduce_to_domain(self, in_links, out_links, crawled_links):
        new_in_links = {}
        for url in in_links:
            original = in_links[url]
            after = set()
            for u in original:
                if u not in crawled_links:
                    print("Weird")
                    domain = self.canonicalizer.get_domain(u)
                    new_u = re.findall("http.*{}".format(domain), u)[0]
                    after.add(new_u)
                else:
                    after.add(u)
            new_in_links[url] = after
        new_out_links = {}
        for url in out_links:
            original = out_links[url]
            after = set()
            for u in original:
                u_s = "https://" + u[7:]
                if u not in crawled_links and u_s not in crawled_links:
                    domain = self.canonicalizer.get_domain(u)
                    after.add("http://" + domain)
                else:
                    if u in crawled_links:
                        after.add(u)
                    else:
                        after.add(u_s)
            new_out_links[url] = after
        return new_in_links, new_out_links


# a = Parser()
# a.initialize("E:/Will/work/NEU/CS 6200/WebCrawler/output/")
# titles = a.title_parse()
# in_links, out_links = a.links_parse()
# # raw_html = a.html_parse()
# # docs, headers = a.doc_parse()
# # raw_html, in_links, out_links = a.json_parse()
#
# new_in_links, new_out_links = a.reduce_to_domain(in_links, out_links, crawled_links)
#
# crawled_links = []
# with open("E:/Will/work/NEU/CS 6200/WebCrawler/output/crawled_links.txt", "r") as f:
#     for line in f:
#         crawled_links.append(line.replace("\n", ""))
# crawled_links = set(crawled_links)
#
# with open("E:/Will/work/NEU/CS 6200/WebCrawler/output/new_in_links.json", "w") as f:
#     for url in new_in_links:
#         json.dump({url: list(new_in_links[url])}, f)
#         f.write("\n")
#
# with open("E:/Will/work/NEU/CS 6200/WebCrawler/output/new_out_links.json", "w") as f:
#     for url in new_out_links:
#         json.dump({url: list(new_out_links[url])}, f)
#         f.write("\n")
# in_links = {i: in_links[i] for i in test}
# out_links = {i: out_links[i] for i in test}
#
# with open("E:/Will/work/NEU/CS 6200/WebCrawler/output/test_in_links.json", "w") as f:
#     json.dump(in_links, f)
#
# with open("E:/Will/work/NEU/CS 6200/WebCrawler/output/test_out_links.json", "w") as f:
#     json.dump(out_links, f)
