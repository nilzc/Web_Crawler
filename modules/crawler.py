import requests
from bs4 import BeautifulSoup
from canonicalization import Canonicalizer
from robots import Robots
from datetime import datetime
import time
import file_io
import re
from frontier import Frontier, FrontierItem


class Crawler:

    def __init__(self):
        self.seed_urls = None
        self.frontier = Frontier()
        self.canonicalizer = Canonicalizer()
        self.all_links = None
        self.crawled_links = set()
        self.count = 0
        self.all_out_links = {}
        self.redirected_map = {}
        self.robots = {}
        self.robots_delay = {}
        self.robots_timer = {}
        self.time_out = 3
        self.total_count = 40000

    def initialize(self, seed_urls):
        self.all_links = set(seed_urls)
        self.seed_urls = seed_urls
        self.frontier.initialize(seed_urls)

    def crawl_control(self):
        file_io.initialize_log()

        current_wave = 0
        while True:
            # if empty, move to next wave
            if self.frontier.is_empty():
                self.frontier.change_wave(current_wave+1)
            # if still empty, finished
            if self.frontier.is_empty():
                self.finish()
                return "Finished"
            current_wave, score, url = self.frontier.frontier_pop()

            # get protocol, domain
            domain = self.canonicalizer.get_domain(url)

            # check robots.txt
            if domain not in self.robots:
                try:
                    robots = Robots("http://" + domain + "/robots.txt")
                    self.robots[domain] = robots
                    if robots.delay > self.time_out:
                        self.robots_delay[domain] = self.time_out
                    else:
                        self.robots_delay[domain] = robots.delay
                    self.robots_timer[domain] = datetime.now()
                except Exception as e:
                    error = "Read robots.txt error:\n{0}\nError: {1}\n\n".format("http://" + domain + "/robots.txt", e)
                    file_io.write_error_info(error)
                    continue

            delay = self.robots_delay[domain]

            # check if can fetch
            if not self.robots[domain].can_fetch(url):
                not_allowed = "Not Allowed: {}\n".format(url)
                print(not_allowed)
                file_io.write_not_allowed(not_allowed)
                continue
            else:
                # politeness
                since_last_crawl = datetime.now() - self.robots_timer[domain]
                if since_last_crawl.total_seconds() < delay:
                    time.sleep(delay - since_last_crawl.total_seconds())
                print("Current: " + url)
                file_io.write_current_link(url)
                # print time interval
                # print((datetime.now() - self.robots_timer[domain]).total_seconds())

                # get page header
                try:
                    url_head = self.get_head(url)
                    if url_head.status_code == 404:
                        error = "Status error:\n{0}\nError code: {1}\n\n".format(url, url_head.status_code)
                        file_io.write_error_info(error)
                        continue
                except Exception as e:
                    error = "Read head error:\n{0}\nError: {1}\n\n".format(url, e)
                    file_io.write_error_info(error)
                    self.robots_timer[domain] = datetime.now()
                    continue
                header = dict(url_head.headers)

                # get content type
                if "content-type" in url_head.headers:
                    content_type = url_head.headers["content-type"]
                else:
                    content_type = "text/html"
                # crawl html type
                if "text/html" not in content_type:
                    continue
                else:
                    # read page
                    try:
                        soup, raw_html, base_url, lang = self.get_page(url)
                        self.robots_timer[domain] = datetime.now()
                        # whether we should crawl, language, black list
                        if not self.page_should_crawl(base_url, lang):
                            continue
                        # multiple redirected url
                        if base_url in self.crawled_links:
                            self.frontier.objects[base_url].in_links.update(self.frontier.objects[url].in_links)
                            error = "Multiple redirected URL:\nURL: {0}\nRedirected URL: {1}\n\n".format(url, base_url)
                            file_io.write_error_info(error)
                            continue
                        else:
                            self.crawled_links.add(base_url)
                            frontier_item = FrontierItem(base_url)
                            frontier_item.in_links = self.frontier.objects[url].in_links
                            self.frontier.objects[base_url] = frontier_item
                            self.redirected_map[url] = base_url
                    except Exception as e:
                        error = "Read page error:\n{0}\nError: {1}\n\n".format(url, e)
                        file_io.write_error_info(error)
                        self.robots_timer[domain] = datetime.now()
                        continue

                    raw_out_links = self.get_out_links(soup)
                    out_links = []

                    # write as ap format
                    text = self.extract_text(soup)
                    if len(soup.select("title")) != 0:
                        title = soup.select("title")[0].get_text()
                    else:
                        title = None
                    file_io.write_ap(base_url, text, header, title)
                    file_io.write_raw_html({base_url: raw_html})

                    for link in raw_out_links:
                        processed_link = self.canonicalizer.canonicalize(base_url, domain, link)
                        file_io.write_canonicalization(link, processed_link)
                        # if link is not empty
                        if len(processed_link) != 0:
                            out_links.append(processed_link)
                            if processed_link not in self.all_links:
                                # new frontier item
                                frontier_item = FrontierItem(processed_link, link)
                                frontier_item.update_in_links(base_url)

                                self.frontier.frontier_put(frontier_item, current_wave+1)
                                self.all_links.add(processed_link)
                            else:
                                # update in links
                                if processed_link in self.redirected_map:
                                    redirected = self.redirected_map[processed_link]
                                    self.frontier.frontier_update_inlinks(redirected, base_url)
                                else:
                                    self.frontier.frontier_update_inlinks(processed_link, base_url)
                    file_io.write_all_out_links({base_url: out_links})
                self.count += 1
                print(self.count, current_wave, url, score)
                file_io.write_log(self.count, current_wave, url, score)
                file_io.write_final_info(len(self.crawled_links), len(self.all_links))
                if self.count == self.total_count:
                    self.finish()
                    print("Finished")
                    return

    def finish(self):
        for url in self.crawled_links:
            file_io.write_crawled_links(url)
            file_io.write_all_in_links({url: list(self.frontier.objects[url].in_links)})
        file_io.write_all_links(self.all_links)

    def get_out_links(self, soup):
        a = soup.select('a')
        out_links = []
        for item in a:
            if item.get('href'):
                out_links.append(item['href'])
        return out_links

    def get_page(self, url: str):
        headers = {"Connection": "close"}
        res = requests.get(url=url, headers=headers, timeout=self.time_out)
        soup = BeautifulSoup(res.text, "lxml")
        try:
            if soup.select("html")[0].has_attr("lang"):
                lang = soup.select("html")[0]['lang']
            else:
                lang = "en"
        except Exception as e:
            error = "Read language error:\n{0}\nError: {1}\n\n".format(url, e)
            file_io.write_error_info(error)
            lang = "en"
        base_url = res.url
        return soup, res.text, base_url, lang

    def get_head(self, url: str):
        headers = {"Connection": "close"}
        head = requests.head(url=url, headers=headers, timeout=self.time_out, allow_redirects=True)
        return head

    def extract_text(self, soup: BeautifulSoup):
        output = ""
        text = soup.find_all("p")
        for t in text:
            new_t = t.get_text()
            new_t = re.sub("\n", "", new_t)
            new_t = re.sub("  +", " ", new_t)
            if len(new_t) == 0:
                continue
            output += "{} ".format(new_t)
        return output

    def page_should_crawl(self, base_url, lang):
        result = True
        # check language
        if "en" not in lang.lower():
            error = "Language error: {0}\nLanguage = {1}\n\n".format(base_url, lang)
            file_io.write_error_info(error)
            result = False
        # check black list
        black_list = [".jpg", ".svg", ".png", ".pdf", ".gif",
                      "youtube", "edit", "footer", "sidebar", "cite",
                      "special", "mailto", "books.google", "tel:",
                      "javascript", "www.vatican.va", ".ogv", "amazon",
                      ".webm"]
        block = 0
        key = ""
        for key in black_list:
            if key in base_url.lower():
                block = 1
                break
        if block == 1:
            error = "Page type error: {0}\nkeyword = {1}\n\n".format(base_url, key)
            file_io.write_error_info(error)
            result = False
        return result


class Node:

    def __init__(self, url: str):
        self.url = url
        self.raw_page = ""
        self.out_links = set()
        self.in_links = set()
