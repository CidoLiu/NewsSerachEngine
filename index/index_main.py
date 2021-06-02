# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 00:04:40 2015

@author: bitjoy.net
"""

from index_module import IndexModule
from datetime import *


if __name__ == "__main__":

    # 抓取新闻数据，提前抓好就行，这里不用每次运行都去抓数据

    # 构建索引
    print('-----start indexing time: %s-----' % (datetime.today()))
    im = IndexModule('../config.ini', 'utf-8')
    im.construct_postings_lists()
