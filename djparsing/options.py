from urllib.parse import urlsplit


class Options(object):
    def __init__(self, meta):
        self.meta = meta
        self.list_domain = list()
        self.image = None
        self.base_domain = None
        self.page_url = list()
        self.data_result = dict()

    @staticmethod
    def get_domain(url):
        return '{0.scheme}://{0.netloc}'.format(urlsplit(url))
