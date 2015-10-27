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

    #页面utf8编码，注释gbk编码设置
    #response.encoding = 'gbk'
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
        self.area_list_url      = "http://www.bjchs.org.cn/map/block_l.jsp"
        self.area_prefix_url    = "http://www.bjchs.org.cn/map/Org_block_l?key_area_code=" # + area_code
        self.org_prefix_url     = "http://www.bjchs.org.cn/map/Org_block_l?key_org_code=" # + org_code
        self.station_prefix_url = "http://service.bjchs.org.cn/gywm.jhtml?" # + station_code


    def run(self):
        for area_code, area_name in self.fetchArea():
            for org_code, org_name in self.fetchOrg(area_code, area_name):
                for station_code, station_name in self.fetchStation(org_code):
                    #默认最后一级都不是agent
                    is_agent = 0
                    self.saveStationList(area_name, org_name, station_code, station_name, is_agent)
                pass

    """
    抓取区县信息，东城区 etc..
    """
    def fetchArea(self):
        content = fetchContent(self.area_list_url)
        dom = BeautifulSoup(content, "html5lib")
        area_wrap = dom.find('select', {'id':'key_area_code'})
        area_all  = area_wrap.findAll('option')
        area_all.pop(0)
        for area in area_all:
            # area_code and area_name
            yield area['value'],unicode(area.string)
        pass


    """
    抓取服务中心信息  大屯社区卫生服务中心 etc..
    """
    def fetchOrg(self, area_code, area_name):
        content = fetchContent(self.area_prefix_url + area_code)
        dom = BeautifulSoup(content, "html5lib")
        org_wrap = dom.find('select', {'id':'key_org_code'})
        org_all  = org_wrap.findAll('option')
        org_all.pop(0)
        for org in org_all:
            #print org
            # org_code and org_name
            org_code = org['value']
            org_name = unicode(org.string).strip()
            if len(org['value'])==6:
                print "Special Station " + org_code + org_name
                is_agent = 0
                #savedata
                self.saveStationList(area_name, '', org_code, org_name, is_agent)
                continue
            else:
                print "Agent Station " + org_code + org_name
                is_agent = 1
                #savedata
                self.saveStationList(area_name, '', org_code, org_name, is_agent)
            yield org_code, org_name
        pass


    def fetchStation(self,station_code):
        content = fetchContent(self.org_prefix_url + station_code)
        dom = BeautifulSoup(content, "html5lib")
        station_wrap = dom.find('select', {'id':'station_key_org_code'})
        station_all  = station_wrap.findAll('option')
        station_all.pop(0)
        for station in station_all:
            #print station
            # station_code and station_name
            yield station['value'],unicode(station.string).strip()
        pass

    def saveStationList(self,area_name, org_name, station_code, station_name, is_agent):
        station = {
            'area'         : area_name,
            'org'          : org_name,
            'name'         : station_name,
            'station_code' : station_code,
            'is_agent'     : is_agent
        }
        print area_name, org_name, station_code, station_name, is_agent
        self.saveData('beijing_shequ', station)

    def parseStation(self):
        for station in self.stationToParse():
            content = fetchContent(self.station_prefix_url + station.station_code)
            dom       = BeautifulSoup(content, "html5lib")
            #parse data
            data_wrap = dom.find('ul', {'class':'sidec'})
            data      = data_wrap.findAll('li')
            new_insurance_wrap = data.pop()
            insurance_wrap     = data.pop()
            insurance_num_wrap = data.pop()
            area_wrap          = data.pop()
            mobile_wrap        = data.pop()
            address_wrap       = data.pop()
            station_data = {
                'new_insurance' : unicode(new_insurance_wrap.find('span').string).strip(),
                'insurance'     : unicode(insurance_wrap.find('span').string).strip(),
                'insurance_num' : unicode(insurance_num_wrap.find('span').string).strip(),
                'mobile'        : unicode(mobile_wrap.find('span').string).strip(),
                'address'       : unicode(address_wrap.find('div').string).strip(),
                'status'        : 1,
            }
            station_data['id'] = station.id
            print station_data
            self.updateData('beijing_shequ', station_data)


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

    def stationToParse(self):
        stations = self.db.query("SELECT * FROM `beijing_shequ` WHERE `status`=%s ORDER BY `id` DESC ", 0)
        for station in stations:
            yield station

if __name__ == "__main__":
    db = Connection(host='localhost', database='spider_test', user='root', password='')
    spider = shequSpider(db)
    spider.parseStation()

