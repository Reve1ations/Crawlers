from bs4 import BeautifulSoup
from bs4.element import Comment

str = '''
<title id="title">尚学堂</title>
<div class='info' float='left'>Welcome to SXT</div>
<div class='info' float='right'>
    <span>Good Good Study</span>
    <a href='www.bjsxt.cn'></a>
    <strong><!--没用--></strong>
</div>
'''
soup = BeautifulSoup(str, 'lxml')
#
# print(soup.title)
# print(soup.div)
#
# print(soup.div.attrs)
# print(soup.div.get('class'))
# print(soup.div['float'])
# print(soup.a['href'])
#
# print(soup.div.string)
# print(type(soup.div.string))
# print(soup.div.text)
#
# if type(soup.strong.string) == Comment:
#     print(soup.strong.string)
#     print(soup.strong.prettify())
# else:
#     print(soup.strong.text)
# print("------------------find_all----------------------")
# print(soup.find_all('title'))
# print(soup.find_all(id='title'))
# print(soup.find_all(class_='info'))
# print(soup.find_all("div", attrs={'float': 'left'}))

str2 = '''
<title id="title">尚学堂</title>
<div class='info' float='left'>Welcome to SXT</div>
<div class='info' float='right'>
    <span>Good Good Study</span>
    <a href='www.bjsxt.cn'>gfsdgs</a>
    <strong><!--没用--></strong>
</div>
'''
# print("--------------------css()---------------------------")
# print(soup.select('title'))
# print(soup.select('#title'))
# print(soup.select('.info'))
# print(soup.select('div span'))
# print(soup.select('div > span'))
# print("kkkkk",soup.select('div')[1].select('a')[0])
# print(soup.select('title')[0].text)


str3 = '''

 <author class="a-author">
            
            <span class="date">05-22 08:25&nbsp;&nbsp;</span>

                            <span class="source">
                    <a href="javascript:;" target="_blank">湖北日报&nbsp;&nbsp;</a>
                </span>
                    </author>
'''

soup = BeautifulSoup(str3, 'lxml')
print("kkkkk", soup.find_all(class_='source')[0].get_text().strip())

