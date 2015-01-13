#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import sys
import os
import string
import htmllib
import urllib
import urlparse
import formatter
from sys import argv
from urllib import urlretrieve
from urllib import urlencode
import urllib2
import cookielib
import re
###################by ht.simple.happy@163.com
import StringIO 
import gzip
###################by ht.simple.happy@163.com

#要生成的文件
targetFile = 'articles.xml'
#登录地址
loginUrl = "http://passport.renren.com/PLogin.do"
#日志列表分页信息
#pageReg = '当前显示1-(\d*)篇/共(\d*)篇'
pageReg = '\d+篇'

#下一篇日志URL正则表达式
#articleUrlNxtReg = 'http://blog.renren.com/GetPreBlog.do\?id=(\d*)&owner=\d*&time=\d*&op=pre' 第一版
#articleUrlNxtReg='http://blog.renren.com/blog/\d+/\d+/preOrNext\?time=\d+\&op=pre' 第二版 by @laoyang945
#articleUrlNxtReg='http://blog.renren.com/blog/\d+/\d+\?from=fanyeOld' 第三版 by ht.simple.happy@163.com
articleUrlNxtReg='http://blog.renren.com/blog/\d+/\d+\?bfrom=\d+'
	
def addtorss(f,name):   
    file=open(name)
    line = file.readlines() 
    # find the title of the blog entry
    title = ''
    createtime = ''
    content = ''
    findBegTag = 0
    #文章里面标题、创建时间、正文的顺序依次
    title = ''
    data = '<title>'
    j = 0
    for eachLine in line:
        j=j+1
        m = re.search(data,eachLine)
        if m is not None:
            break
    strs = line[j-1]
#    n_start = strs.find('<title>')+41
    n_start = strs.find('<title>')+7
    n_end = strs.rfind('</title>')
    title = strs[n_start:n_end]
    
    
# find the time of the blog entry
    time = ''
    data = '"timestamp"'
    j = 0
    for eachLine in line:
        j=j+1
        m = re.search(data,eachLine)
        if m is not None:
            break
    strs = line[j-1]
    n_start = strs.find('span class="timestamp"')+23
    n_end = strs.rfind('<span class="group">')
    time = strs[n_start:n_end]

# find the content of the blog entry  
    content = ''
    data = 'id="blogContent"' 
    i = 0
    for eachLine in line:
        i = i + 1
        m = re.search(data,eachLine)
        if m is not None:
            print "id='blogContent' is not None"
            break
    content = line[i+2]

# find the comment of the blog entry
    
                    
    xmlStr  = '\t<item>\n'
    xmlStr  += '\t\t<title>'+ title + '</title>\n'
    xmlStr  += '\t\t<pubdate>'+ time + '</pubdate>\n'
    divTagIndex = content.rfind('</div>')
    if divTagIndex > 0:
        content = content[0:divTagIndex]
    xmlStr  += '\t\t<content:encoded><![CDATA['+ content + ']]></content:encoded>\n'
    
    xmlStr  += '\t</item>\n'
    f.write(xmlStr) 
    
def main():
# login to xiaonei
    strs=''
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    opener.addheaders = [
      ("User-agent", "Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7"),
      ("Accept","image/png,image/*;q=0.8,*/*;q=0.5"),
			("Host","dj.renren.com"),
			("Referer","http://reg.renren.com/"),
			('Accept-Language', 'zh-CN,zh;q=0.5'),   
			('Accept-Encoding','gzip,deflate'),
			('Accept-Charset', 'GB2312,utf-8;q=0.7,*;q=0.7'),
			('Keep-Alive', '300'),
			('Connection', 'keep-alive'),
			('Cache-Control', 'max-age=0')
			]
            
    UserName=raw_input('your email in renren.com:')
    Password=raw_input('your password:')
    firstPage=raw_input('your first blog\'s address:')
    data = {
            'email':UserName,
            'password': Password,
            'domain':'renren.com',
            'autoLogin':'true',
			      'origURL':"http://www.renren.com/SysHome.do",
			      'submit': '登录'
            }
    urldata = urlencode(data)
    r = opener.open(loginUrl, urldata)
    results = r.read()
    print "Login Successful"
        
    ###################by ht.simple.happy@163.com
    compressedstream = StringIO.StringIO(results)  
    r = gzip.GzipFile(fileobj=compressedstream) 
    results = r.read()    
    ###################by ht.simple.happy@163.com

    r = opener.open(firstPage)
    results = r.read()    
    
    ###################by ht.simple.happy@163.com
    compressedstream = StringIO.StringIO(results)  
    r = gzip.GzipFile(fileobj=compressedstream) 
    results = r.read()    
    ###################by ht.simple.happy@163.com

    open('temp.txt', 'w').write(results)
    
# get the whole article number
    file = open('temp.txt')
    lines = file.readlines()
    file.close()
    article_num = 0
	#find the article num below
    for line in lines:
        m = re.search(pageReg,line)
        if m is not None: 
	    ###by osily<ly50247@gmail.com>
	    article_num= int(re.search('\d+', m.group(0)).group(0))
            #article_num = string.atoi(m.group(0),10)
            break
    print("There are " + str(article_num) + " articles found!")  
            
    #download the articles

    save_file = open(targetFile,'w')
    save_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    addtorss(save_file,'temp.txt')
    
    for k in range(2,article_num+1):
        file = open('temp.txt')
        line = file.readlines()
        file.close()
        mflag=True
        for eachLine in line:
            m = re.search(articleUrlNxtReg,eachLine)
            if m is not None:
                strs = m.group()
                mflag=False
                break
        if mflag:
            print 'failure in  reading previous dialog'
            break
        r = urllib2.urlopen(strs)
        results = r.read()
        ###################by ht.simple.happy@163.com
        compressedstream = StringIO.StringIO(results)  
        r = gzip.GzipFile(fileobj=compressedstream) 
        results = r.read()    
        ###################by ht.simple.happy@163.com         
        print "Downloading the ", k, "th of "+ str(article_num) +" articles"
        open('temp.txt','w').write(results)
        addtorss(save_file,'temp.txt')
    save_file.close()               
	
    os.remove('temp.txt') 
    

if __name__ == '__main__':
    main()

