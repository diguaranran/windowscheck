#coding:utf-8

import ConfigParser
import hashlib
import os
import random, re
import sys
import threading, time, traceback
import xml.dom.minidom
import httplib
import smtplib, mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.Header import Header
from email.mime.image import MIMEImage



#数据对象
class Data:
    def __init__(self, data = None):
        self.data = data

    def get(self):
        return self.data

    def set(self, data):
        self.data = data

def tryExcept(func, *params, **paramMap):
    try:
        return True, func(*params, **paramMap)
    except:
        return False, ''.join(traceback.format_exception(*sys.exc_info()))

def calcMd5(fileName, cacheSize = 32768):
    try:
        m = hashlib.md5()
        f = file(fileName,'rb')
        while True:
            d = f.read(cacheSize)
            if not d:
                break
            m.update(d)
        return m.hexdigest()
    except:
        return None

def calcStrMd5(data, cacheSize = 32768):
    try:
        m = hashlib.md5()
        i = 0
        while True:
            d = data[i:i + cacheSize]
            if not d:
                break
            m.update(d)
            i += cacheSize
        return m.hexdigest()
    except:
        return None

def getTime(style = '%Y-%m-%d %H:%M:%S'):
    return time.strftime(style, time.localtime())

def sendMail(mailFrom, mailTo, mailSubject, mailContent, mailCc = []):
    if type(mailTo) == str:
        mailTo = [mailTo]
    msg = MIMEMultipart()
    msg['From']    = '%s' % mailFrom
    msg['To']      = '%s' % ','.join(mailTo)
    if mailCc:
        msg['Cc']  = '%s' % ','.join(mailCc)
    msg['Subject'] = Header(mailSubject, charset='UTF-8')
    txt = MIMEText(mailContent, _subtype='html',  _charset='UTF-8')
    msg.attach(txt)
    hdl = None
    try:
        hdl = smtplib.SMTP()
        hdl.connect('mail.corp.qihoo.net', 25)
        hdl.sendmail(mailFrom, mailTo, msg.as_string())
        return True
    except:
        import traceback
        print traceback.format_exc()
        return False
    finally:
        if hdl:
            tryExcept(hdl.close)

def encodeXml(data):
    return data.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace("'", '&apos;').replace('"', '&quot;')

def doc2Xml(doc):
    return doc.toxml().replace("'", '&apos;').replace('"', "'").replace('?>', "encoding='utf-8'?>")

def xml2Doc(xmlStr):
    return xml.dom.minidom.parseString(xmlStr)

def setKeyValue(m, ks, v):
    if type(ks) not in (list, tuple):
        ks = [ks]
    p = m
    for k in ks[:-1]:
        if not p.has_key(k):
            p[k] = {}
        p = p[k]
    p[ks[len(ks) - 1]] = v

def appendKeyValue(m, ks, v):
    if type(ks) not in (list, tuple):
        ks = [ks]
    p = m
    for k in ks[:-1]:
        if not p.has_key(k):
            p[k] = {}
        p = p[k]
    if not p.has_key(ks[len(ks) - 1]):
        p[ks[len(ks) - 1]] = []
    p[ks[len(ks) - 1]].append(v)

def getIniMap(iniPath):
    if not os.path.exists(iniPath):
        return {}
    iniMap = {}
    try:
        configure = ConfigParser.RawConfigParser()
        configure.read(iniPath)
        for sec in configure.sections():
            secKey = toSystemStr(sec)
            iniMap[secKey] = {}
            for opt in configure.options(sec):
                optKey = toSystemStr(opt)
                iniMap[secKey][optKey] = toSystemStr(configure.get(sec, opt))
    except:
        pass
    return iniMap

def setIniMap(iniPath, iniMap):
    f = open(iniPath, 'w')
    for sec in iniMap.keys():
        f.write('[%s]\n' % (toLocalStr(sec)))
        for opt in iniMap[sec].keys():
            f.write('%s=%s\n' % (toLocalStr(opt), iniMap[sec][opt]))
    f.close()

def encode(data):
    try:
        return data.encode('utf-8').strip()
    except:
        return ''

def toLocalStr(data):
    try:
        return data.decode('utf-8').encode(sys.getfilesystemencoding()).strip()
    except:
        return ''

def toSystemStr(data):
    try:
        return data.decode(sys.getfilesystemencoding()).encode('utf-8').strip()
    except:
        return ''

def randomInt():
    try:
        return str(random.random()).split('.')[1]
    except:
        return randomInt()

def javaScript(data):
    return "<script language='javascript'>%s</script>" % data

def path2Array(path):
    dir, name = os.path.split(path)
    if dir:
        if re.match(r'^[\\/]+$', dir):
            return [dir, name]
        array = path2Array(dir)
        if name:
            array.append(name)
        return array
    if name:
        return [name]
    return []

def writeLog(data):
    try:
        data = data.decode('utf-8').encode(sys.getfilesystemencoding())
    except:
        pass
    sys.stdout.write('[%s] %s\n' % (getTime(), data))
    sys.stdout.flush()

def handleTimeout(func, timeout, *params, **paramMap):
    while float(timeout) > 0:
        t = time.time()
        rst = func(*params, **paramMap)
        if rst:
            return rst
        time.sleep(0.3)
        timeout -= time.time() - t

def negtive(func, *params, **paramMap):
    return not func(*params, **paramMap)

def doInThread(func, *params, **paramMap):
    class FuncThread(threading.Thread):
        def __init__(self, func, params, paramMap):
            threading.Thread.__init__(self)
            self.func = func
            self.params = params
            self.paramMap = paramMap
            self.finished = False
        def run(self):
            self.result = self.func(*self.params, **self.paramMap)
            self.finished = True
        def isFinished(self):
            return self.finished
    ft = FuncThread(func, params, paramMap)
    ft.start()
    return ft

def parseUrl(url):
    index1 = url.find('://') + 3
    proto = url[:index1 - 3]
    index2 = url.find('/', index1)
    if index2 == -1:
        return proto, url[index1:], '/'
    return proto, url[index1:index2], url[index2:]

def doHttp(url, headers = {}, method = 'GET', body = None):
    proto, host, location = parseUrl(url)
    baseHeaders = {}
    baseHeaders['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    baseHeaders['Accept-Charset'] = 'GBK,utf-8;q=0.7,*;q=0.3'
    baseHeaders['Accept-Language'] = 'zh-CN,zh;q=0.8'
    baseHeaders['Cache-Control'] = 'no-cache'
    baseHeaders['Connection'] = 'keep-alive'
    baseHeaders['Host'] = host
    baseHeaders['Origin'] = '%s://%s' % (proto, host)
    baseHeaders['Pragma'] = 'no-cache'
    baseHeaders['User-Agent'] = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7'
    for k, v in headers.items():
        baseHeaders[k] = v
    conn = None
    try:
        if proto == 'http':
            conn = httplib.HTTPConnection(host)
        else:
            conn = httplib.HTTPSConnection(host)
        conn.request(method, location, body, baseHeaders)
        res = conn.getresponse()
        baseHeaders.clear()
        for k, v in res.getheaders():
            baseHeaders[k] = v
        return res.status, baseHeaders, res.read()
    except:
        pass
    finally:
        if conn:
            conn.close()

def getSvnFileUri(uri, user, pswd):
    dirname, filename = os.path.split(uri)
    p = os.popen3('svn list "%s" --username %s --password %s' % (toLocalStr(dirname), user, pswd))
    if p[2].read():
        return
    for realname in toSystemStr(p[1].read()).strip().split('\n'):
        if realname.lower() == filename.lower():
            return os.path.join(dirname, realname)

def getSvnFileAttr(uri, user, pswd):
    uri = getSvnFileUri(uri, user, pswd)
    if not uri:
        return
    p = os.popen3('svn info "%s" --username %s --password %s' % (toLocalStr(uri), user, pswd))
    if p[2].read():
        return
    rst = re.search('最后修改的时间: ([0-9]{4}(-[0-9]{2}){2} ([0-9]{2}:){2}[0-9]{2})', toSystemStr(p[1].read()), re.S)
    if rst:
        return int(time.mktime(time.strptime(rst.groups()[0], '%Y-%m-%d %H:%M:%S')))

def getSvnFile(uri, user, pswd, path):
    uri = getSvnFileUri(uri, user, pswd)
    if not uri:
        return False
    p = os.popen3('pushd "%s";svn export "%s" --username %s --password %s' % (path, toLocalStr(uri), user, pswd))
    return not p[2].read()

def getSvnListAttr(uri, user, pswd):
    p = os.popen3('svn list "%s" --username %s --password %s' % (toLocalStr(uri), user, pswd))
    if p[2].read():
        return {}
    m = {}
    for filename in toSystemStr(p[1].read()).strip().split('\n'):
        m[filename] = getSvnFileAttr(os.path.join(uri, filename), user, pswd)
    return m

def getSvnList(uri, user, pswd, path):
    p = os.popen3('pushd "%s";svn export "%s" "%s" --force --username %s --password %s' % (os.path.dirname(path), toLocalStr(uri), os.path.basename(path), user, pswd))
    return not p[2].read()
