import requests
import bs4
import time
import random

from retry import requests_retry_session
from retry2 import retry2

class MHGClient:
    def __init__(self, opts):
        self.opts = opts
        self.session = requests.session()
        if 'backoff_factor' in opts.keys():
            self.session = requests_retry_session(
                session=self.session,
                backoff_factor=opts['backoff_factor'])
        self.session.headers.update({
            'User-Agent': opts['user_agent']
        })
        self.chunk_size = opts['chunk_size'] if opts['chunk_size'] else 512
    @property
    def proxy(self):
        if 'proxy' in self.opts.keys():
            return {
                'http': self.opts['proxy'],
                'https': self.opts['proxy']
            }
        else:
            return None
    def get(self, uri: str, **kwargs):
        res = retry2(
            lambda: self.session.get(uri, proxies=self.proxy, **kwargs)
        )
        if 'sleep' in self.opts.keys(): self.sleep()
        return res
    def get_soup(self, uri: str, **kwargs):
        res = self.get(uri, **kwargs)
        return bs4.BeautifulSoup(res.text, 'html.parser')
    def retrieve(self, uri: str, dst: str, **kwargs):
        with open(dst, 'wb') as f:
            res = retry2(
                lambda: self.session.get(uri, stream=True, proxies=self.proxy, **kwargs)
            )
            for chunk in res.iter_content(chunk_size=self.chunk_size):
                if chunk: f.write(chunk)
        if 'sleep' in self.opts.keys(): self.sleep()
    def sleep(self):
        time.sleep(random.randrange(*self.opts['sleep']) / 1000)