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
MONGO_TABLE = 'JR_RM' + time.strftime("%Y%m%d%H%I%S")
db = connnect[MONGO]
error_urls = []
OUT_FILE_NAME = "RM" + time.strftime("%Y%m%d%H%I%S") + ".json"


def get_page(page):
    base_url = 'http://industry.people.com.cn'
    url = 'http://industry.people.com.cn/GB/413887/index' + str(page) + '.html'
    html1 = requests.get(url, headers=headers)
    html1.encoding = html1.apparent_encoding
    html = html1.text
    pattern = re.compile('class="ej_list_box clear"(.*?)class="page_n clearfix"', re.S)
    tem_content = re.findall(pattern, html)
    pattern = re.compile('<li><a href=\'(.*?)\'', re.S)
    urls = re.findall(pattern, html)

    for url in urls:
        url = base_url + url
        parse(url)


def parse(url):
    global error_urls
    try:
        html1 = requests.get(url, headers=headers)
        html1.encoding = html1.apparent_encoding
        html = html1.text

        soup = BeautifulSoup(html, 'lxml')
        title = soup.find_all('title')[0].get_text()
        act_time = soup.select('.box01')[0].get_text().strip()[:17]
        content = soup.select('.box_con')[0].get_text()
        pattern = re.compile('name="keywords".content="(.*?)"', re.S)
        keyword = re.findall(pattern, html)[0]

        pattern = re.compile('name="description".content="(.*?)"', re.S)
        description = re.findall(pattern, html)[0]

        data = {
            'title': title,
            'keyword': keyword,
            'description': description,
            'date': act_time.strip(),
            'content': content,
            'url': url
        }
        save_to_MONGO(data, url)

    except Exception as e:
        print("出错了", e)
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
        print('正在切换,第', i+1, '页')

    # 从MongoDB中取数据
    list_data = []
    data = db[MONGO_TABLE].find()
    for line in data:
        info = dict()
        info["title"] = str(line["title"]).replace("\n", "").replace("  ", "")
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
