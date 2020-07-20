import urllib.robotparser
import urllib.request


class TimeoutRobotFileParser(urllib.robotparser.RobotFileParser):
    def __init__(self, url='', timeout=3):
        super().__init__(url)
        self.timeout = timeout

    def read(self):
        """Reads the robots.txt URL and feeds it to the parser."""
        try:
            f = urllib.request.urlopen(self.url, timeout=self.timeout)
        except urllib.error.HTTPError as err:
            if err.code in (401, 403):
                self.disallow_all = True
            elif err.code >= 400:
                self.allow_all = True
        else:
            raw = f.read()
            self.parse(raw.decode("utf-8").splitlines())


class Robots:

    def __init__(self, url):
        self.url = url
        self.r = self.initialize()
        self.delay = 1.0

        self.get_delay()

    def initialize(self):
        r = TimeoutRobotFileParser()
        r.set_url(self.url)
        r.read()
        return r

    def get_delay(self):
        delay = self.r.crawl_delay(useragent="*")
        if delay is not None:
            self.delay = delay

    def can_fetch(self, new_url):
        return self.r.can_fetch("*", new_url)

# a = TimoutRobotFileParser(timeout=3)
# a.set_url("http://www.miamiherald.com/robots.txt")
# a.read()
