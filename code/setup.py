# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 00:04:40 2015

@author: bitjoy.net
"""

from index_module import IndexModule
from datetime import *
import urllib.request
import configparser

 
if __name__ == "__main__":
    print('-----start time: %s-----'%(datetime.today()))
    
    #抓取新闻数据，提前抓好就行，这里不用每次运行都去抓数据
    
    #构建索引
    print('-----start indexing time: %s-----'%(datetime.today()))
    im = IndexModule('../config.ini', 'utf-8')
    im.construct_postings_lists()
    
    # #推荐阅读
    # print('-----start recommending time: %s-----'%(datetime.today()))
    # rm = RecommendationModule('../config.ini', 'utf-8')
    # rm.find_k_nearest(5, 25)
    # print('-----finish time: %s-----'%(datetime.today()))