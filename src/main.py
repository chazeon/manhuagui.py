import json
from client import MHGClient
from mhg import MHGComic, MHGVolume
import multiprocess.pool

def get_pages(comic: MHGComic):
    for volume in comic.volumes:
        for page in volume.pages:
            yield page

def retrieve_page(page):
    page.retrieve()

if __name__ == '__main__':
    with open('config.json', encoding='utf8') as f:
        opts = json.load(f)
    client = MHGClient(opts)
    comic_uri = input('请输入漫画索引页地址: ')
    comic = MHGComic(comic_uri, opts=opts)
    pool = multiprocess.pool.Pool(1)
    pages = list(get_pages(comic))
    pool.map(retrieve_page, pages)
