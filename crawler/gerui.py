#!/usr/bin/env python
#-*- coding:utf-8 -*-

import requests,time


def getStatus():
    headers = {
        "Pragma"          : "no-cache",
        "Origin"          : "http://m.yaomaiche.com",
        "Accept-Encoding" : "gzip, deflate",
        "Accept-Language" : "zh,en;q=0.8,zh-CN;q=0.6,fr;q=0.4,zh-TW;q=0.2,hr;q=0.2",
        "User-Agent"      : "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4",
        "Content-Type"    : "application/json",
        "Accept"          : "application/json",
        "Cache-Control"   : "no-cache",
        "Referer"         : "http://m.yaomaiche.com/",
        "Connection"      : "keep-alive",
        "__UserKey"       : "userKey 03cd63aa-fc50-45d4-810d-a96c1a301ad9"
    }
    url      = "http://ecmob.yaomaiche.com/api/services/Products/CarGoods/GetCarGoodsSourceInfo"
    payload  = {"CarGoodsId":"9289b42d-34ac-40f7-be79-a58d009dc601","areaId":"9420aade-7fcb-47b3-bac1-ea204d253a40"}
    response = requests.get(url, headers=headers, json=payload)
    data     = response.json()
    
    return  data and data['result']['saleInventory'] or None 

def getTime():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))

if __name__ == "__main__":
    while True:
        status = getStatus()
        if status!= u"售罄":
            mobile = 13262228218
            msg    = "爬虫发现新消息，请速度查看。退订回N"
            smsUrl = "http://service.100xhs.com/sms/send?mobile=%s&message=%s&channel=diexin&timestamp=1453993978&appname=warning&secret=warningooxx&token=5d1b93f7d5981c692f55b743a554144a"%(mobile, msg)
            requests.get(smsUrl)
            print getTime()
            print msg
            print '----------'
        else:
            print getTime()
            print status.encode('utf8')
            print '----------'
        time.sleep(300);
    

