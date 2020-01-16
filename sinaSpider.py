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
MONGO_TABLE = 'JR_XL' + time.strftime("%Y%m%d%H%I%S")
db = connnect[MONGO]
OUT_FILE_NAME = "XL" + time.strftime("%Y%m%d%H%I%S") + ".json"
flag = 0
gx_num = 0


def get_page(page):
    global gx_num
    global flag
    url = 'http://finance.sina.com.cn/roll/index.d.html?cid=56592&page=' + str(page)
    html = requests.get(url, headers=headers).text
    # print(html)
    urls_acticle = []
    pattern = re.compile('<div class="hs01"> </div>(.*?)<div class="hs01"> </div>', re.S)
    content = re.findall(pattern, html)
    pattern_url2 = re.compile('<a href="(.*?)"', re.S)
    urls_b2 = re.findall(pattern_url2, str(content))
    for url in urls_b2:
        urls_acticle.append(url)

    for url in urls_acticle:
        if db[MONGO_TABLE].find_one({'url': url}):
            flag = 1
            print('最新更新：', gx_num, '条')
            break
        else:
            gx_num = gx_num + 1
            parse_page(url)  # 拿到一个页面的所有的url，进行处理


def parse_page(url):
    try:
        act_time = ''
        content = ''
        html1 = requests.get(url, headers=headers)
        html1.encoding = html1.apparent_encoding
        html = html1.text

        soup = BeautifulSoup(html, 'lxml')
        title = soup.find_all('title')[0].get_text()
        act_time_t = soup.select('.date')
        content_t = soup.select('.article')
        pattern = re.compile('name="keywords".content="(.*?)"')
        keyword = re.findall(pattern, html)[0]

        pattern = re.compile('name="description".content="(.*?)"')
        description = re.findall(pattern, html)[0]

        for c in content_t:
            content = content + c.get_text()

        for t in act_time_t:
            act_time = t.get_text()
        data = {
            'title': title,
            'keyword': keyword,
            'description': description,
            'date': act_time,
            'content': content.strip(),
            'url': url
        }
        save_to_MONGO(data, url)
    except IndexError:
        pass


def save_to_MONGO(data, url):
    if db[MONGO_TABLE].insert(data):
        print('正在存储:', url)


def main():
    for i in range(settings.START_PAGE, settings.END_PAGE):
        if flag == 0:
            get_page(i)
            print('切换下一页')
        else:
            break

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
