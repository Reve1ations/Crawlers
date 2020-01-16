import os
import re
import time
from datetime import datetime

import pymongo
import requests
from bs4 import BeautifulSoup
from pandas import json

from . import settings

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'
}
MONGO_URL = 'localhost'
MONGO = 'JR'
connnect = pymongo.MongoClient(MONGO_URL)
now_time = datetime.now()
MONGO_TABLE = 'JR_TX' + str(now_time).strip()
db = connnect[MONGO]
error_urls = []
OUT_FILE_NAME = "TX" + str(now_time).format("%Y-%m-%d-%H_%M_%S") + ".json"


def get_second_page(page):
    url = 'http://stock.qq.com/l/stock/shsgs/list20150423134920_' + str(page) + '.htm'
    html1 = requests.get(url, headers=headers)
    html1.encoding = html1.apparent_encoding
    html = html1.text

    pattern = re.compile('class="mod newslist"(.*?)class="pageNav"', re.S)
    info_act = re.findall(pattern, html)

    pattern = re.compile('a target="_blank" href="(.*?)\"', re.S)
    urls = re.findall(pattern, str(info_act))
    for url in urls:
        print(url)
        parse_page_2(url)  # 拿到一个页面的所有的url，进行处理


def parse_page_2(url):
    content = ''
    try:
        global error_urls
        html1 = requests.get(url, headers=headers)
        html1.encoding = html1.apparent_encoding
        html = html1.text

        soup = BeautifulSoup(html, 'lxml')
        title = soup.find_all('title')[0].get_text()
        data = soup.find_all(class_='pubTime article-time')[0].get_text()
        content_t = soup.find_all(style="TEXT-INDENT: 2em")
        for c in content_t:
            content = content + c.get_text()
        pattern = re.compile('name="keywords".content="(.*?)"', re.S)
        keyword = re.findall(pattern, html)[0]
        pattern = re.compile('name="Description".content="(.*?)"', re.S)
        description = re.findall(pattern, html)[0]
        data = {
            'title': title,
            'keyword': keyword,
            'description': description,
            'date': data,
            'content': content,
            'url': url
        }
        if 'return' in data['content']:
            pass
        else:
            save_to_MONGO(data, url)
    except Exception as e:
        print('报错了', e)
        error_urls.append(url)


def save_to_MONGO(data, url):
    if db[MONGO_TABLE].insert(data):
        print('正在存储:', url)


def main():
    for i in range(26, 51):
        get_second_page(i)
        time.sleep(2)
        print('正在切换,第', i, '页')
    with open(os.path.join(os.getcwd(), 'error_urls.txt'), 'w', encoding='utf-8') as f:
        f.write(str(error_urls))
    f.close()

    # 从MongoDB中取数据！
    list_data = []
    data = db[MONGO_TABLE].find()
    for line in data:
        info = {}
        info["title"] = str(line["title"]).replace(" | 腾讯网", "").replace("\n", "").replace("  ", "")
        info["content"] = str(line["content"]).replace("\n", "").replace("  ", "")
        list_data.append(info)

    fid = open(os.path.join(settings.CRAWED_DATA_DIR, OUT_FILE_NAME), "w", encoding="utf-8")
    for i in range(len(list_data)):
        out_file = json.dumps(list_data, ensure_ascii=False)
        fid.write(out_file)
    fid.close()
    print(error_urls)


if __name__ == '__main__':
    main()
