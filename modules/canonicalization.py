import re
import file_io


class Canonicalizer:

    def get_domain(self, url: str):
        domain = re.findall("//[^/]*\w", url, flags=re.IGNORECASE)[0]
        domain = domain[2:]
        return domain

    def canonicalize(self, base_url: str, domain: str, url: str):
        if "\\" in url:
            result = re.sub("\\\\+", "/", url.encode("unicode_escape").decode())
        else:
            result = url
        result = re.sub("[\n\t ]*", "", result)
        try:
            # exception
            if domain == "www.vatican.va" or domain == "www.ysee.gr" or domain == "www.biblegateway.com":
                return ""
            if domain == "web.archive.org" and "en/member-churches" in result:
                return ""
            if domain == "penelope.uchicago.edu" and "E/Roman/Texts" in result:
                result = re.sub("E/.*", result, base_url)

            # remove anchor
            result = re.sub("#.*", "", result)
            if not re.findall("\w", result):
                return ""

            # handle something like "xxxx.html"
            if re.match("^[\w~]+[^:]*$", result):
                result = re.sub("/\w*[^/]*\w*$", "/" + result, base_url)
            elif re.match("^\w+[^/]+\w$", result):
                result = re.sub("/\w*[^/]*\w*$", "/" + result, base_url)
            elif re.match("^\./\w+[^:]*[\w/]$", result):
                result = re.sub("/\w*[^/]*\w*$", result[1:], base_url)
            elif re.match("^\?[^/]*", result):
                result = base_url + result

            # relative path ../../../ssss.ssd
            if re.match("^(?:\.{2}/)+\w+.*", result):
                replace = re.findall("\.{2}/\w+.*", result)[0][2:]
                level = len(re.findall("\.{2}", result))
                folders = re.findall("/\w+(?:\.\w+)*", base_url)
                target = "".join(folders[-level-1:])
                result = re.sub(target, replace, base_url)
            # non html
            black_list = [".jpg", ".svg", ".png", ".pdf", ".gif",
                          "youtube", "edit", "footer", "sidebar", "cite",
                          "special", "mailto", "books.google", "tel:",
                          "javascript", "www.vatican.va", ".ogv", "amazon",
                          ".webm"]
            for key in black_list:
                if key in result.lower():
                    return ""

            # remove port
            if re.match("https", result, flags=re.IGNORECASE) is not None:
                result = re.sub(":443", "", result)
            elif re.match("http", result, flags=re.IGNORECASE) is not None:
                result = re.sub(":80", "", result)
            # http/https case
            result = re.sub("http", "http", result, flags=re.IGNORECASE)
            result = re.sub("https", "http", result, flags=re.IGNORECASE)

            # missing domain
            if re.match("^/.+", result) is not None:
                result = "http://" + domain + result
            # missing protocal
            elif re.match("^//.+", result) is not None:
                result = "http:" + result
            # multiple slashes
            duplicate_slashes = re.findall("\w//+.", result)
            if len(duplicate_slashes) != 0:
                for dup in duplicate_slashes:
                    replace_str = dup[0] + "/" + dup[-1]
                    result = re.sub(dup, replace_str, result)

            # domain lower case
            find_domain = re.findall("//[^/]*\w", result)
            find_domain = find_domain[0]
            lower_case_domain = find_domain.lower()
            result = re.sub(find_domain, lower_case_domain, result)

            # convert empty path
            if re.match(".*com$", result) is not None:
                result += "/"

            # convert % triplets to upper case, (%7E, "~")
            percent_code = re.findall("%\w{2}", result)
            for p in percent_code:
                result = re.sub(p, p.upper(), result)
            return result
        except Exception as e:
            error = "Canonicalization error:\nbase_url = '{0}'\nurl = '{1}'\ndomain = '{2}'\n{3}\n\n".format(
                base_url, url, domain, str(e))
            print(error)
            file_io.write_error_info(error)
            return ""

# base_url = "https://christian.net/pub/resources/christian-history.html"
# url = "text\history\nicene.html"
# domain = "www.iclnet.org"
#
# a = Canonicalizer()
# print(a.canonicalize(base_url, domain, url))
