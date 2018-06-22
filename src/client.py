import requests
import bs4

class MHGClient:
    def __init__(self, opts):
        self.opts = opts
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': opts['user_agent']
        })
        self.chunk_size = opts['chunk_size'] if opts['chunk_size'] else 512
    def get(self, uri: str, **kwargs):
        return self.session.get(uri, **kwargs)
    def get_soup(self, uri: str, **kwargs):
        res = self.get(uri, **kwargs)
        return bs4.BeautifulSoup(res.text, 'html.parser')
    def retrieve(self, uri: str, dst: str, **kwargs):
        with open(dst, 'wb') as f:
            res = self.session.get(uri, stream=True, **kwargs)
            for chunk in res.iter_content(chunk_size=self.chunk_size):
                if chunk: f.write(chunk)