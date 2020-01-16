import json
import os
import re
import time

import pymongo
import requests
from bs4 import BeautifulSoup

from . import settings

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'
}
MONGO_URL = 'localhost'
MONGO = 'JR'
connnect = pymongo.MongoClient(MONGO_URL)
MONGO_TABLE = 'JR_MJ' + time.strftime("%Y%m%d%H%I%S")
db = connnect[MONGO]
OUT_FILE_NAME = "MJ" + time.strftime("%Y%m%d%H%I%S") + ".json"


def get_page(page):
    url = 'http://www.nbd.com.cn/columns/346/page/' + str(page)
    html = requests.get(url, headers=headers).text

    pattern = re.compile('u-li-items.*?<a href="(.*?)"', re.S)
    urls = re.findall(pattern, html)

    for url in urls:
        parse(url)


error_urls = []
error_num = 0


def parse(url):
    global error_urls
    global error_num
    try:
        d_html = requests.get(url, headers=headers).text
        soup = BeautifulSoup(d_html, 'lxml')
        title = soup.find_all('title')[0].get_text()
        act_time = soup.select('.time')[0].get_text()
        content = soup.select('.g-articl-text')[0].get_text()
        pattern = re.compile('name="Keywords".content="(.*?)"', re.S)
        keyword = re.findall(pattern, d_html)[0]

        pattern = re.compile('name="Description".content="(.*?)"', re.S)
        description = re.findall(pattern, d_html)[0]

        data = {
            'title': title,
            'keyword': keyword,
            'description': description.strip(),
            'date': act_time.strip(),
            'content': content,
            'url': url
        }
        save_to_MONGO(data, url)
    except Exception as e:
        error_num = error_num + 1
        if error_num < 5:
            print(e)
            time.sleep(3)
            parse(url)
        else:
            error_urls.append(url)
            pass


def save_to_MONGO(data, url):
    if db[MONGO_TABLE].insert(data):
        print('正在存储:', url)


def main():
    global error_urls
    for i in range(settings.START_PAGE, settings.END_PAGE):
        get_page(i)
        time.sleep(2)
        print('正在切换,第', i + 1, '页')

    # 从MongoDB中取数据
    list_data = []
    data = db[MONGO_TABLE].find()
    for line in data:
        info = {}
        info["title"] = str(line["title"]).replace(" | 每经网", "").replace("\n", "").replace("  ", "")
        info["content"] = str(line["content"]).replace("\n", "").replace("  ", "")
        list_data.append(info)

    if os.path.exists(settings.CRAWED_DATA_DIR) is False:
        os.makedirs(settings.CRAWED_DATA_DIR)
    if os.path.exists(os.path.join(settings.CRAWED_DATA_DIR, time.strftime("%Y%m%d"))) is False:
        os.makedirs(os.path.join(settings.CRAWED_DATA_DIR, time.strftime("%Y%m%d")))

    data_path_inner = time.strftime("%Y%m%d") + "\\" + OUT_FILE_NAME
    data_path_out = os.path.join(settings.CRAWED_DATA_DIR, data_path_inner)

    fid = open(data_path_out, "w", encoding="utf-8")
    out_file = json.dumps(list_data, ensure_ascii=False)
    fid.write(out_file)
    fid.close()
    print(error_urls)


if __name__ == '__main__':
    main()
