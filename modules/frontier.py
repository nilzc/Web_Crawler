import re
import file_io
import queue
import math


class Frontier:

    def __init__(self):
        self.queue = queue.PriorityQueue()
        self.objects = {}
        self.waves = {}

    def initialize(self, seed_urls):
        self.waves[0] = set()
        for url in seed_urls:
            frontier_item = FrontierItem(url)
            frontier_item.compute_score()
            self.objects[url] = frontier_item
            self.waves[0].add(url)
            self.queue.put((0, frontier_item.score, url))
    
    def initialize_rest(self, rest_urls: list):
        for q in rest_urls:
            self.queue.put(q)

    def frontier_pop(self):
        return self.queue.get()

    def frontier_put(self, frontier_item, wave):
        url = frontier_item.url
        self.objects[url] = frontier_item
        if wave not in self.waves:
            self.waves[wave] = set()
        self.waves[wave].add(url)

    def frontier_update_inlinks(self, url, in_link):
        self.objects[url].update_in_links(in_link)

    def is_empty(self):
        return self.queue.empty()

    def change_wave(self, wave):
        if wave not in self.waves:
            return
        examine = []
        cutoff = 1.04
        for url in self.waves[wave]:
            frontier_item = self.objects[url]
            frontier_item.compute_score()
            if frontier_item.score > cutoff:
                continue
            examine.append((frontier_item.score, url))
            self.queue.put((wave, frontier_item.score, url))
        examine.sort()
        file_io.write_wave_score(wave, examine)


class FrontierItem:

    def __init__(self, url: str, raw_url=None):
        self.url = url
        self.raw_url = raw_url
        self.key_words = \
            ["catholic", "church", "commandments", "catechism",
             "jesus", "christ", "bishop", "pope", "sacred", "sacrament",
             "saint", "peter", "god", "theology", "relig", "papacy",
             "vatican", "doctrin", "canonical", "roman", "holy",
             "cardinal", "heaven", "baptism", "see"]
        self.in_links = set()
        self.score = 0
        self.text = ""
        self.raw_html = ""

    def compute_score(self):
        # key word hits
        keyword_hits = 0
        for k in self.key_words:
            if self.raw_url is not None:
                if len(re.findall(k, self.raw_url, flags=re.IGNORECASE)) != 0:
                    keyword_hits += 1
            else:
                if len(re.findall(k, self.url, flags=re.IGNORECASE)) != 0:
                    keyword_hits += 1
        keyword_score = math.exp(-keyword_hits)
        in_links_score = math.exp(-len(self.in_links))
        self.score = keyword_score + in_links_score

    def update_in_links(self, url: str):
        self.in_links.add(url)

