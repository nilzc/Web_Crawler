import os
import json


def initialize_log():
    log_files = ["canonicalization", "wave_score", "error", "not_allowed", "current_links", "log"]
    for file_name in log_files:
        path = "./log/{}.txt".format(file_name)
        if os.path.exists(path):
            os.remove(path)

    output_files = ["out_links.json", "documents.txt", "in_links.json", "final.txt", "raw_html.json", "all_links.txt",
                    "crawled_links.txt"]
    for file_name in output_files:
        path = "./output/{}".format(file_name)
        if os.path.exists(path):
            os.remove(path)


def write_canonicalization(url, processed_url):
    with open("./log/canonicalization.txt", "a", encoding="utf-8") as f:
        f.write("{0},    {1}\n".format(url, processed_url))


def write_ap(url: str, text: str, header: dict, title=None):
    with open("./output/documents.txt", "a", encoding="utf-8") as f:
        f.write("<DOC>\n")
        f.write("<DOCNO>{}</DOCNO>\n".format(url))
        if title is not None:
            f.write("<HEAD>{}</HEAD>\n".format(title))
        f.write("<HEADER>{}</HEADER>\n".format(json.dumps(header)))
        f.write("<TEXT>\n")
        f.write(text + "\n")
        f.write("</TEXT>\n")
        f.write("</DOC>\n")


def write_raw_html(raw_html: dict):
    with open("./output/raw_html.json", "a") as f:
        json.dump(raw_html, f)
        f.write("\n")


def write_wave_score(wave, wave_score: list):
    with open("./log/wave_score.txt", "a", encoding="utf-8") as f:
        for line in wave_score:
            f.write("{0}, {1}, {2}\n".format(wave, line[1], line[0]))


def write_all_out_links(out_links: dict):
    with open("./output/out_links.json", "a", encoding="utf-8") as f:
        json.dump(out_links, f)
        f.write("\n")


def write_all_in_links(in_links: dict):
    with open("./output/in_links.json", "a", encoding="utf-8") as f:
        json.dump(in_links, f)
        f.write("\n")
        
        
def write_error_info(error: str):
    with open("./log/error.txt", "a", encoding="utf-8") as f:
        f.write(error)


def write_not_allowed(not_allowed: str):
    with open("./log/not_allowed.txt", "a", encoding="utf-8") as f:
        f.write(not_allowed)


def write_final_info(crawled_links: int, found_links: int):
    with open("./output/final.txt", "w", encoding="utf-8") as f:
        f.write("Number of crawled links: {0}, Number of discovered links: {1}\n".format(crawled_links, found_links))


def write_current_link(url: str):
    with open("./log/current_links.txt", "a", encoding="utf-8") as f:
        f.write("{}\n".format(url))


def write_log(count, wave, url, score):
    with open("./log/log.txt", "a", encoding="utf-8") as f:
        f.write("{0}, {1}, {2}, {3}\n".format(count, wave, url, score))


def write_all_links(all_links):
    with open("./output/all_links.txt", "a", encoding="utf-8") as f:
        for line in all_links:
            f.write(line)
            f.write("\n")


def write_crawled_links(url):
    with open("./output/crawled_links.txt", "a") as f:
        f.write(url)
        f.write("\n")
