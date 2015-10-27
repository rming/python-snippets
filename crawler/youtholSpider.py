#!/usr/bin/env python
#-*- coding:utf-8 -*-

import time, requests, logging, threading, re 
from database import Connection
from pyquery import PyQuery as pq



log_format = '%(filename)s [%(asctime)s] [%(levelname)s] %(message)s'    
logging.basicConfig(
    format  = log_format,
    datefmt = '%Y-%m-%d %H:%M:%S %p',
    level   = logging.DEBUG
) 
"""
logging.basicConfig(
    filename = 'youtholSpider.log', 
    filemode = 'w', 
    level    = logging.DEBUG
) 
"""

class youtholSpider:
    def __init__(self,db):
        self.db = db
        self.baseUrl  = "http://youthol.cn"
        self.indexUrl = "http://youthol.cn/news/2/"
        self.pageUrl  = "http://youthol.cn/news/2/default%d.aspx"
        self.pagecurrent, self.pageTotal = self.fetchIndex()

    def fetchIndex(self):
        d = pq(url=self.indexUrl)
        __, __, navbar = d('.newslist table')
        __, pages      = pq(navbar)('td')
        __, counter    = pq(pages).text().split(' ')[0:2]
        return counter.split('/')

    """
    @todo 获取更新时什么时候停止
    """
    def fetchArticleList(self):
        for page in range(1, int(self.pageTotal)+1):
            d = pq(url=self.pageUrl % page)
            articleTale, __, __ = d('.newslist table')
            articleList = pq(articleTale)('a')
            for article  in articleList:
                articleData = {}
                articleData['title'] = pq(article)('a').text()
                articleData['link'] = pq(article)('a').attr('href')
                __, __, __, newsId          = articleData['link'].split('/')
                articleData['news_id'], __, = newsId.split('.')
                self.saveData('youthol', articleData)

    """
    @todo 下载图片
    """
    def doFetchContentJob(self):
        for article in self.getTodoList():
            r = requests.get(self.baseUrl + article.link)
            r.encoding='gb2312'
            #author's email in raw html code
            authorEmail = ''
            m = re.match("([\s\S]*)mailto:'(.*)'([\s\S]*)", r.text)
            if m:
                authorEmail = m.group(2)

            m = re.match("([\s\S]*)<script language='javascript'>window.location=(.*)</script>([\s\S]*)", r.text)
            if m: continue

            d = pq(r.text)
            authorLink  = d('#sour')('a')
            author      = authorLink.text()
            """
            authorHref  = authorLink.attr('href')
            if authorHref: __, authorEmail = authorHref.split(':')
            """

            articleMeta = d('#sour') or d('#H2')
            viewsScript   = articleMeta('script')
            viewsResult   =  pq(url=self.baseUrl + pq(viewsScript).attr('src'))
            __, views, __ = viewsResult.html().split("'")

            source, author, editor, created_at = ['', '', '',  '00-00-00 00:00'] 
            pattern = "(.*)来源：(.*)作者：(.*)浏览：(.*)".decode("utf8")
            m = re.match(pattern, articleMeta.text())
            if m:
                created_at = m.group(1)
                source     = m.group(2)
                author     = m.group(3)

            articleContent = d('#H3>div').html()
            editorInfo     = d('.col-sm-offset-10').text()
            if not editorInfo: 
                editorInfo = d('#H4>div').text()
                editorInfo = len(editorInfo)<20 and editorInfo or ''
            if editorInfo: __, editor = editorInfo.split(u'：')

            articleData = {
                'id'           : article.id,
                'created_at'   : created_at.strip(),
                'views'        : views,
                'source'       : source.strip(),
                'editor'       : editor,
                'author'       : author.strip(),
                'author_email' : authorEmail,
                'content'      : articleContent,
            }
            self.updateData('youthol', articleData)

    def getTodoList(self):
        return self.db.query("SELECT id,link FROM `youthol` WHERE `content` IS NULL")

    def saveData(self, tableName, data):
        dataGet = self.db.get("SELECT * FROM `"+ tableName +"` WHERE `news_id`=%s limit 0,1", data['news_id'])
        if not dataGet:
            dataId = self.db.insert(tableName, **dict(data))
        else:
            dataId = dataGet.id
        pass
        self.db.commit()
        return dataId

    def updateData(self, table_name, data):
        if 'id' in data.keys():
            for key in data.keys():
                affect = self.db.execute('update '+ table_name+' set '+ key +'=%s where id=%s',unicode(data[key]),data['id'])
                self.db.commit()
            return affect
        else:
            return 0

if __name__ == "__main__":
    db = Connection(host='localhost', database='spider', user='root', password='root')
    spider = youtholSpider(db)
    spider.doFetchContentJob()
    #spider.fetchArticleList()


