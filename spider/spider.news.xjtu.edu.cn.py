# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 18:32:55 2020

@author: LiuDongjin

【爬虫】爬取交大新闻网主页新闻栏目的所有新闻，以xml格式存入本地。

交大新闻网已改版，2021/6/2代码已适配新版交大新闻网。
"""

from bs4 import BeautifulSoup
import urllib.request
import xml.etree.ElementTree as ET
import configparser
from datetime import *
import time
import urllib.parse
import socketß
from socket import timeout
from os import listdir

user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
headers = {'User-Agent': user_agent}
# values = {'name': 'Michael Foord',
#          'location': 'Northampton',
#          'language': 'Python' }
# data = urllib.parse.urlencode(values)
# data = data.encode('ascii')

keyword = '交'  # 用于判断乱码，一般来说，交大新闻中肯定包括了‘交’
root = 'http://news.xjtu.edu.cn'


def get_one_page_news(page_url):
    '''获取某一新闻列表页上的全部新闻摘要[url, title]
    Args:
        page_url:新闻列表页面的URL
    Returns:
        返回当前页面上所有新闻列表List[List[]]，列表中每一个元素为一条新闻的[url, title]
    '''
    # page_url = 'http://news.xjtu.edu.cn/zyxw/1703.htm'

    req = urllib.request.Request(page_url, headers=headers)

    try:
        response = urllib.request.urlopen(req, timeout=10)
        html = response.read()
    except socket.timeout as err:
        print('socket.timeout')
        print(err)
        return []
    except Exception as e:
        print("-----%s:%s %s-----" % (type(e), e, page_url))
        return []

    soup = BeautifulSoup(html, "html.parser")

    news_pool = []
    # news_list = soup.find('div', class_='i_left')
    items = soup.find_all('div', class_='fr zws')
    # print(items)
    for i, item in enumerate(items):
        if len(item) == 0:
            continue

        a = item.find('a')
        title = a.get('title')
        url = a.get('href')
        # if root in url:
        #     url = url[len(root):]
        if '..' in url:
            url = url.replace('..', root)  # ../info/1004/4750.htm
        else:
            url = root + '/' + url  # info/1033/137388.htm

        news_info = [url, title]
        news_pool.append(news_info)

    return news_pool


def get_news_pool(news_category):
    '''获取新闻列表池
    Args:
        news_category:为一个固定列表，指定需要爬取的新闻分类
    Returns:
        返回一个新闻列表List[List[]]，列表中每一个元素为一条新闻的[url, title]
    '''
    news_pool = []
    for category in news_category:
        first_url = root + '/' + category + '.htm'
        news_pool += get_one_page_news(first_url)
        print('Extracting news urls at ' + first_url)
        page_index = 1705
        page_counter = 0
        while page_counter < 5:
            # http://news.xjtu.edu.cn/xyzs/21.htm
            page_url = 'http://news.xjtu.edu.cn/' + \
                category+'/'+str(page_index)+'.htm'
            print('Extracting news urls at '+category+str(page_index))
            news_pool += get_one_page_news(page_url)
            page_index -= 1
            page_counter += 1
    return news_pool


def crawl_news(news_pool, min_body_len, doc_dir_path, doc_encoding):
    '''
    开始爬取新闻
    Args:
        news_pool:新闻列表池[[url, title], ...]
        min_body_len:最短新闻长度限制
        doc_dir_path:结果文件存储路径
        doc_encoding:结果文件编码方式
    '''
    files = listdir(doc_dir_path)
    i = len(files)
    news_pool_len = len(news_pool)
    for n, news in enumerate(news_pool):
        print('%d/%d' % (n, news_pool_len))
        req = urllib.request.Request(news[0], headers=headers)
        try:
            response = urllib.request.urlopen(req, timeout=10)
            html = response.read()
        except socket.timeout as err:
            print('socket.timeout')
            print(err)
            print("Sleeping for 1 minute")
            time.sleep(60)
            continue
        except Exception as e:
            print("--1--- %s:%s %s -----" % (type(e), e, news[0]))
            print("Sleeping for 1 minute")
            time.sleep(60)
            continue

        soup = BeautifulSoup(html, "html.parser")
        [s.extract() for s in soup('script')]  # 去除script

        try:
            spans = soup.find('div', class_="shfffff").find_all('span')
        except Exception as e:
            pass

        date = ''
        for span in spans:
            temp_text = span.get_text().strip()
            if temp_text.startswith('日期'):
                date = temp_text.replace('日期：', '')

        try:
            ps = soup.find('div', class_="v_news_content").find_all('p')
        except Exception as e:
            print("--2--- %s: %s -----" % (type(e), news[0]))
            print("Sleeping for 1 minute")
            time.sleep(60)
            continue

        body = ''
        for p in ps:
            cur = p.get_text().strip()
            if cur == '':
                continue
            body += '\t' + cur + '\n'
        body = body.replace(" ", "")

        if keyword not in body:
            continue

        if len(body) <= min_body_len:
            continue

        doc = ET.Element("doc")
        # news_id = 'xjtunews ' + "%d" %(i)
        ET.SubElement(doc, "id").text = "%d" % (i)
        ET.SubElement(doc, "url").text = news[0]
        ET.SubElement(doc, "title").text = news[1]
        ET.SubElement(doc, 'datetime').text = date
        ET.SubElement(doc, 'body').text = body
        tree = ET.ElementTree(doc)
        tree.write(doc_dir_path + "%d.xml" %
                   (i), encoding=doc_encoding, xml_declaration=True)
        i += 1
        if i % 500 == 0:
            print("Sleeping for 3 minute")
            time.sleep(180)


if __name__ == '__main__':
    print('-----start time: %s-----' % (datetime.today()))
    config = configparser.ConfigParser()
    config.read('../config.ini', 'utf-8')

    # test_news_pool = get_one_page_news('http://news.xjtu.edu.cn/zyxw/1703.htm')
    # print(test_news_pool)
    # crawl_news(test_news_pool, 20, config['DEFAULT']
    #            ['doc_dir_path'], config['DEFAULT']['doc_encoding'])

    # news_category = ['zyxw','jyjx','xyzs', 'kydt']
    news_category = ['zyxw']
    news_pool = get_news_pool(news_category)
    # news_pool = list(set(news_pool))
    print('Starting to crawl %d xjtunews' % len(news_pool))

    crawl_news(news_pool, 20, config['DEFAULT']
               ['doc_dir_path'], config['DEFAULT']['doc_encoding'])
    print('-----done! time: %s-----' % (datetime.today()))
