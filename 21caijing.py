import requests
import re
from bs4 import BeautifulSoup
import pymongo
import urllib.request
import chardet
import json

headers = {
    'User-Agent': "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
}

MONGO_URL = 'localhost'
MONGO = "21caijing"
connect = pymongo.MongoClient(MONGO_URL)
MONGO_TABLE = '21caijing'
db = connect[MONGO]

def getdata( url):
    html = requests.get(url,headers)
    raw_data = urllib.request.urlopen(url).read()
    charset = chardet.detect(raw_data)
    encoding = charset['encoding']
    html.encoding = encoding
    # print(html.text)

    pattern = re.compile('<h5 class="title"><a href=(.*?) target=')
    article_url = re.findall(pattern,html.text)
    print(article_url)

    json_data = []
    for item in article_url:
        item = item.strip("\"")
        parse(item, json_data)


def parse(url,json_data):
    try:
        html = requests.get(url, headers)
        raw_data = urllib.request.urlopen(url).read()
        charset = chardet.detect(raw_data)
        encoding = charset['encoding']
        html.encoding = encoding
        html = html.text
        # print(html)

        #Title
        pattern_title = re.compile('<h1 class="artcleTitle">(.*?)</h1>')
        title = re.findall(pattern_title,html)
        if len(title) == 0:
            return
        else:
            title = title[0]
        # print(title)

        # origin
        soup = BeautifulSoup(html, 'lxml')
        # patter_origin = re.compile('<span class="articleSource">(.*?)<span ')
        # origin = re.findall(patter_origin)
        origin = soup.find(class_ = 'articleSource')
        # print(origin)
        if len(origin) == 0:
            return
        else:
            origin = origin.get_text().strip()
        # print(origin)

        #Description
        patter_description = re.compile('<div class="articlSum"><strong>核心提示：</strong>(.*?)</div>')
        description = re.findall(patter_description, html)
        if len(description) == 0:
            return
        else:
            description = description[0]
        # print(description)

        # Content
        # patter_content = re.compile('<td class="articleContentTD">(.*?)</td></tr>')
        # content = re.findall(patter_content, html)
        content = soup.find(class_='articleContentTD')
        if len(content) == 0:
            return
        else:
            content = content.get_text().strip()
        # print(content)

        # Select
        if len(content) and 4 < len(content.strip()) < 20000:
            content = re.sub("\r\n|\r|\n|\t|,", " ", content)
            data = {
                'title': title.strip(),
                'origin': title.strip(),
                'description': title.strip(),
                'content': content.strip()
            }
            json_data.append(data)

        save_data(json_data, url, "json")

    except Exception as e:
        print(url,"find a error")
        print(e)
        pass

def save_data(data, url,chanel="mongo"):
    if "json" == chanel:
        with open("E://crawed_data//getfile.json", mode="w", encoding="utf-8") as fp:
            json.dump(data,fp,ensure_ascii = False)
            fp.close()
    else:
        if db[MONGO_TABLE].insert(data):
            print('正在存储:', url)

if __name__ == '__main__':
    # url = "http://news.21so.com/gushi/2.html"
    for i in range(2, 7000):
        url = 'http://news.21so.com/gushi/{page}.html'.format(page=i)
    getdata(url)