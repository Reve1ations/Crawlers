import json
import os
import re
import time

import requests
import pymongo
from bs4 import BeautifulSoup

from SVM_model import settings

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'
}
MONGO_URL = 'localhost'
MONGO = 'JR'
connnect = pymongo.MongoClient(MONGO_URL)
MONGO_TABLE = 'JR_SYS' + time.strftime("%Y%m%d%H%I%S")
db = connnect[MONGO]
error_urls = []
OUT_FILE_NAME = "SYS" + time.strftime("%Y%m%d%H%I%S") + ".json"


def get_page(page):
    base_url = 'http://news.toocle.com'
    url = 'http://news.toocle.com/list/c-3511---' + str(page) + '.html'
    html = requests.get(url, headers=headers).content.decode('utf-8')

    pattern = re.compile('行业动态</a>] <a href="(.*?)"', re.S)
    urls = re.findall(pattern, html)

    for url in urls:
        url = base_url + url
        parse_page(url)  # 拿到一个页面的所有的url，进行处理


def parse_page(url):
    global error_urls
    try:
        html1 = requests.get(url, headers=headers)
        html1.encoding = html1.apparent_encoding
        html = html1.text
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find_all('title')[0].get_text()
        act_time_t = soup.select('.text2')[0].get_text()
        if '21ic' in act_time_t:
            act_time = act_time_t.replace('21ic', '')
        else:
            act_time = act_time_t
        if act_time.startswith('2'):
            pass
        else:
            for i in act_time:
                if i == '2':
                    break
                else:
                    act_time = act_time.replace(i, '')
        content = soup.select('.print4')[0].get_text()
        pattern = re.compile('name="keywords".content="(.*?)"', re.S)
        keyword = re.findall(pattern, html)[0]
        pattern = re.compile('name="description".content="(.*?)"', re.S)
        description = re.findall(pattern, html)[0]
        data = {
            'title': title,
            'keyword': keyword,
            'description': description,
            'date': act_time.strip(),
            'content': content.strip(),
            'url': url
        }
        save_to_MONGO(data, url)
        # print(data)
    except Exception as e:
        print('出错了', e)
        error_urls.append(url)
        pass


def save_to_MONGO(data, url):
    if db[MONGO_TABLE].insert(data):
        print('正在存储:', url)


def main():
    for i in range(settings.START_PAGE, settings.END_PAGE):
        get_page(i)
        time.sleep(2)
        print('正在切换,第', i, '页')

    # 从MongoDB中取数据
    list_data = []
    data = db[MONGO_TABLE].find()
    for line in data:
        info = {}
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


if __name__ == '__main__':
    main()
