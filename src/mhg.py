import requests
from client import MHGClient
import urllib
import re
import lzstring
import json
import node
import copy
import os

class MHGComic:
    def __init__(self, uri: str, client: MHGClient = None, opts = None):
        self.uri = uri
        self.client = client if client else MHGClient(opts)
        self.volumes = list(self.get_volumes())
    def get_volumes(self):
        comic_soup = self.client.get_soup(self.uri)
        header = comic_soup.select_one('.book-detail > .book-title > h1').text
        sub_header = comic_soup.select_one('.book-detail > .book-title > h2').text
        title = '{header}: {sub_header}'.format(
            header=header,
            sub_header=sub_header
        )
        anchors = comic_soup.select('.chapter-list > ul > li > a')
        for anchor in anchors:
            link = anchor.get('href')
            volume_name = str(next(anchor.select_one('span').children))
            volume = MHGVolume(urllib.parse.urljoin(self.uri, link), title, volume_name, self.client)
            print(volume)
            yield volume

class MHGVolume:
    def __init__(self, uri: str, title: str, volume_name: str, client: MHGClient):
        self.uri = uri
        self.title = title
        self.volume_name = volume_name
        self.client = client
        self.pages_opts = self.get_pages_opts()
        self.pages = list(self.get_pages())
    def __repr__(self):
        return '<MHGVolume [{title} - {volume_name}]>'.format(
            title=self.title,
            volume_name=self.volume_name,
            uri=self.uri
        )
    def get_pages_opts(self):
        res = self.client.get(self.uri)
        raw_content = res.text
        res = re.search(r'<script type="text\/javascript">window\["\\x65\\x76\\x61\\x6c"\](.*\)) <\/script>', raw_content).group(1)
        lz_encoded = re.search(r"'([A-Za-z0-9+/=]+)'\['\\x73\\x70\\x6c\\x69\\x63'\]\('\\x7c'\)", res).group(1)
        lz_decoded = lzstring.LZString().decompressFromBase64(lz_encoded)
        res = re.sub(r"'([A-Za-z0-9+/=]+)'\['\\x73\\x70\\x6c\\x69\\x63'\]\('\\x7c'\)", "'%s'.split('|')"%(lz_decoded), res)
        code = node.get_node_output(res)
        pages_opts = json.loads(re.search(r'^SMH.imgData\((.*)\)\.preInit\(\);$', code).group(1))
        return pages_opts
    def get_pages(self):
        for i, f in enumerate(self.pages_opts['files']):
            page_opts = copy.deepcopy(self.pages_opts)
            del page_opts['files']
            page_opts['page_num'] = i + 1
            page_opts['file'] = f
            page_opts['referer'] = self.uri
            page_opts['title'] = self.title
            page_opts['volume_name'] = self.volume_name
            yield MHGPage(page_opts, self.client)

class MHGPage:
    def __init__(self, opts, client: MHGClient):
        self.opts = opts
        self.client = client
    @property
    def uri(self):
        return urllib.parse.urljoin(
            self.client.opts['image_base'],
            urllib.parse.quote(
                self.opts['path'] + self.opts['file'],
                encoding='utf8'
            )
        )
    @property
    def dir_name(self):
        return '[{title}][{chapter_name}]'.format(
            title=self.opts['bname'],
            chapter_name=self.opts['cname']
        )
    @property
    def storage_file_name(self):
        return '{page_num}-{file_name}'.format(
            page_num='%02d' % self.opts['page_num'],
            file_name=self.opts['file']
        )
    def retrieve(self):
        dir_path = os.path.join(self.client.opts['download_dir'], self.dir_name)
        file_path = os.path.join(dir_path, self.storage_file_name)
        if os.path.exists(file_path): return
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self.client.retrieve(
            self.uri,
            file_path,
            params={
                'cid': self.opts['cid'],
                'md5': self.opts['sl']['md5']
            },
            headers={
                'Referer': self.opts['referer']
            }
        )

   

