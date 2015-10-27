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


"""
reload(sys)
sys.setdefaultencoding('utf-8')
"""

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
    r = requests.get(url, headers=headers)

    log_message("Http request   end %s" % url)
    return r.text


def log_message(format, *args):
    print format % args

class hospitalSpider:
    '''
    分地区抓取医院数据
    '''
    def __init__(self,db):
        if not db:
            return
        self.db = db
        self.base_url  = "http://yyk.familydoctor.com.cn"
        self.index_url = "http://yyk.familydoctor.com.cn/addarea.html"

        self._start = {}
        self._start['area_uri'],self._start['page_uri'],self._start['hospital_url'] = self.getStage()
        """

        #手动指定开始位置
        self._start = {
            'area_uri'     : '/addarea_51_0_0_0_1.html',
            'page_uri'     : '/addarea_51_0_0_0_1.html',
            'hospital_url' : 'http://yyk.familydoctor.com.cn/3964/',
        }

        #禁用中断恢复
        self._start = {
            'area_uri'     : None,
            'page_uri'     : None,
            'hospital_url' : None
        }
        """

    def fetchHospitalList(self):
        #area_uri 即列表页面首页，可以是（省份/城市/地区）医院列表
        for province_id, city_id, area_uri in self.areaList():
            #page_uri 是所有列表页，通过列表页首页（分页）获得
            for page_uri in self.hospitalPagination(area_uri):
                #本页是否已经全部抓取（足够10条）
                if self.isPageGot(page_uri): self.resetStartAt();continue;
                #是医院地址
                for hospital_url in self.getHospitalsUrl(page_uri):
                    self.getHospital(province_id, city_id, area_uri, page_uri, hospital_url)
                    #抓完一个休息一下
                    time.sleep(0.5)
        self.fixHospitalErrorData()
        log_message('Good Job!')

    def fixHospitalErrorData(self):
        for hospital_id, province_id, city_id, area_uri, page_uri, hospital_url in self.getErrorHospitals():
            self.updateHospital(province_id, city_id, area_uri, page_uri, hospital_url, hospital_id)



    def getHospital(self, province_id, city_id, area_uri, page_uri, hospital_url):
        #是否已经抓取
        if self.isHospitalExisted(hospital_url):
            return False
        #获得医院数据
        _hospital = self.parseHospital(province_id, city_id, area_uri, page_uri, hospital_url)
        #保存数据
        self.saveHospital(_hospital)

    def updateHospital(self, province_id, city_id, area_uri, page_uri, hospital_url, hospital_id):
        _hospital = self.parseHospital(province_id, city_id, area_uri, page_uri, hospital_url)
        _hospital.update({'id':hospital_id})
        self.updateData('hospitals', _hospital)



    def areaList(self):
        content = fetchContent(self.index_url)
        dom = BeautifulSoup(content, "html5lib")
        provinces = dom.findAll('div', {'class' : 'item'})
        for province in provinces:
            province_link = province.find('div',{'class':'itemTitle'}).find('a')
            province_name = unicode(province_link.string)
            province_uri  = province_link['href']
            #provinces except "全国"
            if province_name == u"全国": continue
            province_id = self.saveData('provinces', {'name': province_name})
            #cities
            cities = province.find('div', {'class':'subitem'})
            if not cities: continue
            for city_link in cities.findAll('a'):
                city_name = unicode(city_link.string)
                #city except "亚洲"
                if city_name == u"亚洲": continue
                city_id   = self.saveData('cities', {'name': city_name, 'parent_id': province_id})
                city_uri  = city_link['href']
                if not self.isStartAt('area_uri', city_uri): continue
                #用于查询“市级医院列表”
                yield province_id, city_id, city_uri
            #遍历完成本省“市级医院列表”后,返回“省级医院列表”
            if not self.isStartAt('area_uri', province_uri): continue
            yield province_id, None, province_uri


    def hospitalPagination(self, area_uri):
        index_uri = area_uri.split('.')[0].split('_')
        page_min  = index_uri.pop()

        content = fetchContent(self.base_url + area_uri)
        soup = BeautifulSoup(content, "html5lib")
        last_link = soup.select('.endPage a.last')
        if len(last_link)>=1:
            last_link = last_link[0]
            last_uri  = unicode(last_link['href']).split('.')[0].split('_')
            page_max  = last_uri.pop()
        else:
            page_max = page_min
        #generate page uri
        for num in range(int(page_min), int(page_max) + 1):
            index_uri.append(unicode(num))
            page_uri = '_'.join(index_uri) + ".html"
            #启始标记
            if not self.isStartAt('page_uri', page_uri): index_uri.pop();continue
            yield page_uri
            index_uri.pop()


    def getHospitalsUrl(self, page_uri):
        content = fetchContent(self.base_url + page_uri)
        soup = BeautifulSoup(content, "html5lib")
        listContent = soup.find('div', {'class' : 'listContent'})
        if listContent:
            hospitals  = listContent.findAll('div', {'class' : 'listItem'})
            for hospital in hospitals:
                title_link = hospital.find('h3', {'class':'summary'}).find('a')
                if title_link:
                    hospital_url = title_link['href']
                    #启始标记
                    if not self.isStartAt('hospital_url', hospital_url): continue
                    yield hospital_url

    def parseHospital(self, province_id, city_id, city_uri, page_uri, hospital_url):
        #如果还未抓取，则抓取信息
        _hospital = {}
        _hospital['url']         = hospital_url
        _hospital['province_id'] = province_id
        _hospital['city_id']     = city_id
        _hospital['page_uri']    = page_uri
        _hospital['city_uri']    = city_uri

        #get html content
        home_page    = fetchContent(hospital_url)
        detail_page  = fetchContent(hospital_url + 'detail/')
        map_page     = fetchContent(hospital_url + 'map/')

        #parse content
        _hospital_home   = self._parseHospitalHome(home_page)
        _hospital_detail = self._parseHospitalDetail(detail_page)
        _hospital_map    = self._parseHospitalMap(map_page)

        #update hospital dict
        _hospital.update(_hospital_home)
        _hospital.update(_hospital_detail)
        _hospital.update(_hospital_map)

        return _hospital

    def _parseHospitalDetail(self, content):
        _hospital = {}
        dom = BeautifulSoup(content, "html5lib")
        basic_wrap = dom.find('div', {'class' : 'mBasicInfo'})
        if basic_wrap:
            dl_list = basic_wrap.find('div', {'class' : 'moduleContent'})
            if dl_list:
               dds = dl_list.select('dl dd')
               dds = dds[0:4]
               if len(dds) == 4:
                   _level, _insurance, _type, _kind = dds
                   _level = _level.find('span', {'itemprop':"hospitalGrade"})
                   _hospital['level']     = unicode(_level.string)
                   _hospital['insurance'] = unicode(_insurance.string)
                   _hospital['type']      = unicode(_type.string)
                   _hospital['kind']      = unicode(_kind.string)

            tsks = dl_list.select('dl.tsks a')
            if tsks:
                _hospital['tsks'] = unicode(','.join(t.string for t in tsks))

        #description
        description = dom.find('div', {'itemprop' : 'description'})
        if description:
            _hospital['description'] = ''.join(unicode(content).strip() for content in description.contents)

        return _hospital

    def _parseHospitalMap(self, content):
        _hospital = {}
        soup = BeautifulSoup(content, "html5lib")
        dd_list = soup.select('div.mYydz .moduleContent dl dd')

        if dd_list:
            _address, _phone, _mail_num, _fax_num, _email, _routes = dd_list
            _hospital['address']  = unicode(_address.string).strip()
            _hospital['mail_num'] = unicode(_mail_num.string).strip()
            _hospital['fax_num']  = unicode(_fax_num.string).strip()
            _hospital['routes']   = ''.join(unicode(content).strip() for content in _routes.contents)

            _email_link = _email.find('a')
            if _email_link:
                _hospital['email'] = unicode(_email_link.string)

            _website = _phone.find('a',{'class':'telA'})
            if _website:
               _hospital['site'] = unicode(_website['href'])

        return _hospital

    def _parseHospitalHome(self, content):
        _hospital = {}
        soup = BeautifulSoup(content, "html5lib")
        h_header = soup.find('div', {'class': 'subLogo'})
        if h_header:
            _name = h_header.find('h1')
            if _name:
                _hospital['name']  = unicode(_name.string).strip()

            _nick_name = h_header.find('strong')
            if _nick_name:
                _hospital['nick_name']  = unicode(_nick_name.string).strip(u'（').strip(u'）')

        h_intro = soup.find('div', {'class': 'introPic'})
        if h_intro:
            _photo = h_intro.find('img')
            if _photo:
                _hospital['photo']  = unicode(_photo['src'])

            intro_info = h_intro.findAll('dl')
            if intro_info:
                contacts = intro_info.pop()
                if contacts:
                    _phone_site = contacts.findAll('dd')
                    if _phone_site:
                        _site  = _phone_site.pop()
                        if _site:
                            _site_link = _site.find('a')
                            if _site_link:
                                _hospital['site']  = unicode(_site_link['href'])
                        _phone = _phone_site.pop()
                        if _phone:
                            _hospital['phone']  = unicode(_phone.string).strip()

        return _hospital


    def isStartAt(self, k, v):
        if k in self._start.keys():
            if self._start[k] == None:
                return True
            if self._start[k] == v:
                self._start[k] = None
                return True
            else:
                return False
        else:
            return True
    def resetStartAt(self):
        self._start = {
            'area_uri'     : None,
            'page_uri'     : None,
            'hospital_url' : None
        }

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

    def saveHospital(self, data):
        data_get = self.db.get("SELECT * FROM `hospitals` WHERE `url`=%s limit 0,1", data['url'])
        if not data_get:
            data_id = self.db.insert('hospitals', **dict(data))
        else:
            data_id = data_get.id
        pass
        self.db.commit()
        return data_id

    def getStage(self):
        hospital = self.db.get("SELECT * FROM `hospitals`  ORDER BY `id` DESC limit 0,1")
        if hospital:
            return hospital.city_uri, hospital.page_uri, hospital.url
        else:
            return None, None, None

    def getErrorHospitals(self):
        #三个 IS NULL 分别对应没有获取到三个页面
        hospitals = self.db.query("SELECT * FROM `hospitals` WHERE `photo` IS NULL OR `address` IS NULL OR `description` IS NULL OR `name`=''")
        for hospital in hospitals:
            log_message('Error Hospital %s ', hospital.url)
            yield hospital.id, hospital.province_id, hospital.city_id, hospital.city_uri, hospital.page_uri, hospital.url

    def isHospitalExisted(self, hospital_url):
        print hospital_url
        hospital = self.db.get("SELECT * FROM `hospitals` WHERE url=%s limit 0,1", hospital_url)
        if hospital != None:
            log_message('Hospital existed %s', hospital_url)
            return True
        else:
            return False

    def isPageGot(self, page_uri):
        count = self.db.count("SELECT count(*) FROM `hospitals` WHERE page_uri=%s", page_uri)
        if count==10:
            log_message('Page pass %s', page_uri)
            return True
        else:
            return False


if __name__ == "__main__":
    db = Connection(host='localhost', database='python_spider_test', user='root', password='root')
    spider = hospitalSpider(db)
    spider.fetchHospitalList()

