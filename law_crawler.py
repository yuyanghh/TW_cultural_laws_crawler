# send request and parse html
import requests as rq
from bs4 import BeautifulSoup
# calulate keyword frequence
import pandas as pd

# segment chinese
import jieba
# import jieba.analyse
jieba.set_dictionary('./jieba_dict/include_dict.txt')
exclude_dict = './jieba_dict/exclude_dict.txt'
# jieba.analyse.set_stop_words('./jieba_dict/exclude_dict.txt')
# FIXME: 待研究，成功後可省略remove_stop_words()


# act_url = 'https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=P0050025'
act_url = 'https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=H0170014'
response = rq.get(act_url)
html_doc = response.text
soup = BeautifulSoup(response.text, 'lxml')
# print(soup.title)  # 把 tag 抓出來
# print('---')
# print(soup.title.name)  # 把 title 的 tag 名稱抓出來
# print('---')
# print(soup.title.string)  # 把 title tag 的內容欻出來
# print('---')
# print(soup.title.parent.name)  # title tag 的上一層 tag
# print('---')
# print(soup.a)  # 把第一個 <a></a> 抓出來
# print('---')
# print(type(soup.a))
# print('---')
# print(soup.find_all('div', class_='char-2'))
# print('---')
# print(soup.find_all('div', class_=['char-2', 'col-no']))
# print(soup.find_all('a'))  # 把所有的 <a></a> 抓出來

act_name = soup.find(id='hlLawName').string
act_link = 'https://law.moj.gov.tw/LawClass/' + \
    soup.find(id='hlLawName').get('href')
act_amend_date = soup.find(id='trLNNDate').find('td').string
act_type = soup.select('#trLNNDate ~ tr > td')[0].string
print('法規名稱：' + act_name)
print('法規連結：act_link')
print('法規修正日期：' + act_amend_date)
print('法規類別：' + act_type)


def check_self_with_classname(self, classname):
    if(type(self).__name__ == 'Tag'):
        return self.has_attr('class') and classname in self['class']
    else:
        return False


def get_article_content(self):
    article_contents = self.contents
    return article_contents[1].get_text()


def remove_stop_words(keyword_list):
    with open(exclude_dict, 'r') as f:
        stop_words = f.readlines()
    stop_words = [stop_word.rstrip() for stop_word in stop_words]
    new_keyword_list = []
    for keyword in keyword_list:
        if keyword not in stop_words:
            new_keyword_list.append(keyword)
    return new_keyword_list


def segment_keyword(text, cut_all=False):
    return remove_stop_words(jieba.lcut(text, cut_all))


def count_keyword_freq(keyword_list):
    keyword_df = pd.DataFrame(keyword_list, columns=['keyword'])
    keyword_df['count'] = 1
    keyword_freq = keyword_df.groupby(
        'keyword')['count'].sum().sort_values(ascending=False)
    keyword_freq = pd.DataFrame(keyword_freq)
    return keyword_freq


law_content_list = soup.find('div', class_='law-reg-content').children
current_chapter = ''
for law_content in law_content_list:
    if check_self_with_classname(law_content, 'char-2'):
        if current_chapter != law_content.string:
            current_chapter = law_content.string
    elif check_self_with_classname(law_content, 'row'):
        article_nr = law_content.select('.col-no > a')[0].string
        article_content = law_content.select('.col-data')[0].get_text()
        keyword_list = segment_keyword(article_content)
        keyword_freq = count_keyword_freq(keyword_list)
        keyword_freq.to_csv('./result/' + act_name + '_' +
                            current_chapter + '_' + article_nr + '.csv')
        print(current_chapter, article_nr, article_content, keyword_list)

# chapters = soup.find_all('div', class_='char-2')

# for chapter in chapters:
#     current_article = chapter.find_next_sibling()
#     while check_self_with_classname(current_article, 'row'):
#         chapter_name = chapter.string
#         article_nr = current_article.contents[0].find('a').string
#         article_content = get_article_content(current_article)
#         keyword_list = segment_keyword(article_content)
#         clean_keyword_list = remove_stop_words(keyword_list)
#         print(chapter_name, article_nr, article_content)
#         print('------')
#         print(clean_keyword_list)
#         print('------')
#         # print(chapter.string, current_article.contents[0].find(
#         # 'a').string, current_article.contents[1].get_text())
#         current_article = current_article.find_next_sibling()
