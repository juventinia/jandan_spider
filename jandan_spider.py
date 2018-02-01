#coding = utf8

import requests
from bs4 import BeautifulSoup
import re
import hashlib
import base64
import os
import time
import random

class Jandan(object):
    def __init__(self):
        self.headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Host':'jandan.net',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        }

        '''self.proxies = {
            'http':'http://180.118.33.201'
        }'''
    #解析目标js地址并反悔目标函数的参数
    def target_js(self, res):

        #找到js源地址
        js_address = re.search('.*<script\ssrc=\"\/\/(cdn.jandan.net\/static\/min.*?)\"><\/script>.*', res)
        js = 'http://' + js_address.group(1)
        print(js)
        self.headers['host'] = 'cdn.jandan.net'
        r_js = requests.get(url=js, headers=self.headers)
        print(r_js.status_code)

        #找到目标函数的参数变量,f_函数中第二个参数
        jsFile = re.search('.*f_\w+\(e,\"(\w+)\".*\)', r_js.text)
        paras = jsFile.group(1)

        #获取源html中f_函数的第一个参数(e)
        soup = BeautifulSoup(res, 'lxml')
        args = []
        html = soup.select('.img-hash')

        for each in html:
            args.append(each.text)

        return args, paras


    def md5(self, arg):
        md5 = hashlib.md5()
        md5.update(arg.encode('utf8'))
        return md5.hexdigest()

    def decode_base64(self, data):
        missing_padding = 4 - len(data) % 4
        if missing_padding:
            data += '=' * missing_padding
        return base64.b64decode(data)

    #源js解析函数转换成python执行
    def parse(self, args, paras):
        q = 4
        constant = self.md5(paras)
        o = self.md5(constant[0:16])
        n = self.md5(constant[16:32])
        l = args[0:q]
        c = o + self.md5(o + l)
        imgHash = args[q:]
        k = self.decode_base64(imgHash)
        h = list(range(256))

        b = list(range(256))

        for g in range(0, 256):
            b[g] = ord(c[g % len(c)])

        f = 0
        for g in range(0, 256):
            f = (f + h[g] + b[g]) % 256
            tmp = h[g]
            h[g] = h[f]
            h[f] = tmp

        result = ""
        p = 0
        f = 0
        for g in range(0, len(k)):
            p = (p + 1) % 256
            f = (f + h[p]) % 256
            tmp = h[p]
            h[p] = h[f]
            h[f] = tmp
            result += chr(k[g] ^ (h[(h[p] + h[f]) % 256]))
            
        result = result[26:]

        return result


    #spider
    def spider(self, page):
        os.mkdir('jandan')
        os.chdir('E:\kira\spider_test\jandan')

        start_url = 'http://jandan.net/ooxx'
        r = requests.get(url=start_url, headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        origin_page = soup.find('span', class_='current-comment-page')
        pages = origin_page.get_text()
        start_page = int(pages.replace('[', '').replace(']', ''))

        for page_count in range(page):
            target_page = start_page - page_count
            url = 'http://jandan.net/ooxx/' + 'page-{}#comments'.format(target_page)
            print(url)
            self.headers['host'] = 'jandan.net'
            response = requests.get(url, headers=self.headers, timeout=3)
            parse1, parse2 = self.target_js(response.text)

            #实际图片地址列表解析
            links = []
            for hash in parse1:
                mark = self.parse(hash, parse2)
                links.append(mark)


            self.headers['host'] = 'wx2.sinaimg.cn'
            #图片保存到文件
            print('正在下载第{}页'.format(target_page))
            for each in links:
                real_url = 'http:' + each
                img = requests.get(real_url, headers=self.headers).content
                filename = each.split('/')[-1]
                print('正在下载' + filename)
                with open(filename, 'wb') as f:
                    f.write(img)

                time.sleep(random.randint(2, 4))



jandan = Jandan()
jandan.spider(2)
