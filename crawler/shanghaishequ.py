#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, os.path,requests,time
if os.path.dirname(__file__):
    _cwd = os.path.dirname(__file__)
    sys.path.append(_cwd)
    os.chdir(_cwd)
from random import choice
from bs4 import BeautifulSoup
from database import Connection



def fetchContent(url):
    log_message("Http request start %s" % url)
    UserAgents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)',
        'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50'
    ]
    headers = {
        'User-Agent': choice(UserAgents)
    }
    response = requests.get(url, headers=headers)

    log_message("Http request   end %s" % url)

    response.encoding = 'gbk'
    return response.text


def log_message(format, *args):
    print format % args

class shequSpider:
    '''
    抓取地区数据
    '''
    def __init__(self,db):
        if not db:
            return
        self.db = db
        self.base_url  = "http://www.wsjsw.gov.cn/wsj/n473/n2001/u1ai87440.html"


    def fetchShequ(self):
        content = fetchContent(self.base_url)
        dom = BeautifulSoup(content, "html5lib")
        shequ_all = dom.select('#Zoom tbody tr')
        for shequ in shequ_all:
            shequData = {}
            columns = shequ.select('td')
            if (len(columns)==6):
                currentQuxian = columns[1].string
            shequData['quxian']  = unicode(currentQuxian).strip()
            shequData['fax_num']     = unicode(columns.pop().string).strip()
            shequData['phone']   = unicode(columns.pop().string).strip()
            shequData['address'] = unicode(columns.pop().string).strip()
            shequData['name']    = unicode(columns.pop().string).strip()

            self.saveData('shequ', shequData)


    #######- Data -########

    def updateData(self, table_name, data):
        if 'id' in data.keys():
            for key in data.keys():
                affect = self.db.execute('update '+ table_name+' set '+ key +'=%s where id=%s',unicode(data[key]),data['id'])
                self.db.commit()
            return affect
        else:
            return 0

    def saveData(self, table_name, data):
        data_get = self.db.get("SELECT * FROM `"+ table_name +"` WHERE `name`=%s limit 0,1", data['name'])
        if not data_get:
            data_id = self.db.insert(table_name, **dict(data))
        else:
            data_id = data_get.id
        pass
        self.db.commit()
        return data_id


if __name__ == "__main__":
    db = Connection(host='localhost', database='spider_test', user='root', password='')
    spider = shequSpider(db)
    spider.fetchShequ()

