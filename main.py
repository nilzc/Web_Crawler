from crawler import Crawler
from es import ES

# seed_urls = ["http://en.wikipedia.org/wiki/Catholic_Church",
#              "http://en.wikipedia.org/wiki/Christianity",
#              "http://en.wikipedia.org/wiki/Ten_Commandments_in_Catholic_theology"
#              ]
# # seed_urls = ["http://chirp.io",
# #              "http://chirp.io",
# #              "http://www.adherents.com/Religions_By_Adherents.html"]
#
# crawler = Crawler()
# crawler.initialize(seed_urls)
#
# crawler.crawl_control()

my_es = ES()
my_es.initialize()
my_es.es_control()
