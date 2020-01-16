import requests
import re
from bs4 import BeautifulSoup
import pymongo

headers = {
    'User-Agent': "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
}

MONGO_URL = 'localhost'
MONGO = 'GP'
connnect = pymongo.MongoClient(MONGO_URL)
MONGO_TABLE = 'GP'
db = connnect[MONGO]


def save(_str):
    with open("E://crawed_data//getfile.csv", mode="w", encoding="utf-8") as f:
        f.write("title,content\n")
        for i in range(len(_str)):
            f.write(_str[i])
            f.write("\n")
        f.close()


error_urls = []
error_num = 0


def parse(url):
    global error_urls
    global error_num
    try:
        pattern = re.compile("[0-9]+")
        html = requests.get(url, headers).text
        pattern_title = re.compile('<a href="/list,.*?.html">(.*?)</a>')
        if len(re.findall(pattern_title, html)) == 0:
            return
        else:
            title = re.findall(pattern_title, html)[0]

        soup = BeautifulSoup(html, 'lxml')
        # title = soup.find_all(id="zwconttbt")[0].get_text()
        if len(soup.find_all(id="zwconbody")) == 0:
            return
        else:
            content = soup.find_all(id="zwconbody")[0].get_text()

        # if pattern.findall(content) and len(content)<150 and len(content)>4:
        if pattern.findall(content) and 4 < len(content.strip()) < 200:
            # print(title.strip())
            # print(content.strip())
            title = re.sub("\r\n|\r|\n|\t|,", " ", title)
            content = re.sub("\r\n|\r|\n|\t|,", " ", content)
            data = {
                'title': title.strip(),
                'content': content.strip()
            }
            save_to_MONGO(data, url)
    except Exception as e:
        print(url,'a error find')
        pass


def save_to_MONGO(data, url):
    if db[MONGO_TABLE].insert(data):
        print('正在存储:', url)


def getData(url):
    html = requests.get(url, headers).text
    # print(html)
    pattern = re.compile('] <a href="(.*?)" title=')
    article_url = re.findall(pattern, html)

    for i in article_url:
        u = 'http://guba.eastmoney.com' + i
        parse(u)


if __name__ == '__main__':
    for i in range(1, 7000):
        url = 'http://guba.eastmoney.com/default,0_{page}.html'.format(page=i)
        getData(url)
