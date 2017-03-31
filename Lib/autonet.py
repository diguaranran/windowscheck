#coding:gbk

import autoutil
import httplib
import MySQLdb
import os
import paramiko
import stat

#sftp访问对象
class SftpAccessor:
    def __init__(self, host, user, pswd, port = 22):
        self.host = host
        self.user = user
        self.pswd = pswd
        self.port = port

    def open(self):
        try:
            ssh = paramiko.Transport((self.host, self.port))
            ssh.connect(username = self.user, password = self.pswd)
            sftp = paramiko.SFTPClient.from_transport(ssh)
            self.conn = sftp, ssh
            return True
        except:
            return False

    def close(self):
        autoutil.tryExcept(self.conn[0].close)
        autoutil.tryExcept(self.conn[1].close)

    def list(self, path, dirPaths, filePaths):
        attrs = autoutil.tryExcept(self.conn[0].listdir_attr, path)
        if autoutil.isExcept(attrs):
            return False
        for attr in attrs:
            tmpPath = path.rstrip('/') + '/' + attr.filename
            if stat.S_ISDIR(attr.st_mode):
                dirPaths.append(tmpPath)
            else:
                filePaths.append(tmpPath)
        return True

    def getFileSize(self, filePath):
        fileSize = -1
        try:
            fileSize = self.conn[0].stat(filePath).st_size
        except:
            pass
        return fileSize

    def walk(self, path, filePaths):
        dirPaths = []
        if not self.list(path, dirPaths, filePaths):
            return False
        for dirPath in dirPaths:
            self.walk(dirPath, filePaths)
        return True

    def mkdir(self, path):
        rootPath = '/'
        while True:
            subPath = path[len(rootPath):]
            if not subPath:
                break
            rootPath += '/' in subPath and subPath[:subPath.find('/') + 1] or subPath
            rst = autoutil.tryExcept(self.conn[0].stat, rootPath)
            if not autoutil.isExcept(rst):
                continue
            rst = autoutil.tryExcept(self.conn[0].mkdir, rootPath)
            if autoutil.isExcept(rst):
                return False
        return True

    #path为远程目录或文件,localPath为本地目录
    def download(self, path, localPath):
        attr = autoutil.tryExcept(self.conn[0].stat, path)
        if autoutil.isExcept(attr):
            return False
        filePaths = []
        if stat.S_ISREG(attr.st_mode):
            filePaths.append(path)
            path = os.path.dirname(path)
        elif not self.walk(path, filePaths):
            return False
        if not os.path.exists(localPath):
            os.makedirs(localPath)
        for filePath in filePaths:
            localDirPath, localFileName = os.path.split(os.path.normpath(filePath[len(path):].lstrip('/')))
            localDirPath = localDirPath and os.path.join(localPath, localDirPath) or localPath
            if not os.path.exists(localDirPath):
                os.makedirs(localDirPath)
            rst = autoutil.tryExcept(self.conn[0].get, filePath, os.path.join(localDirPath, localFileName))
            if autoutil.isExcept(rst):
                return False
        return True

    #path为远程目录,localPath为本地目录或文件
    def upload(self, path, localPath):
        localFilePaths = []
        if os.path.isfile(localPath):
            localFilePaths.append(localPath)
            localPath = os.path.dirname(localPath)
        else:
            for localDirPath, localDirNames, localFileNames in os.walk(localPath):
                localFilePaths.extend([os.path.join(localDirPath, localFileName) for localFileName in localFileNames])
        createdDirPaths = set()
        for localFilePath in localFilePaths:
            dirPath, fileName = os.path.split(localFilePath[len(localPath):].lstrip('\\').replace('\\', '/'))
            dirPath = dirPath and path.rstrip('/') + '/' + dirPath or path
            if dirPath not in createdDirPaths:
                if not self.mkdir(dirPath):
                    return False
                createdDirPaths.add(dirPath)
            self.conn[0].put(localFilePath, dirPath.rstrip('/') + '/' + fileName)
        return True

#数据库连接对象
class DbAccessor:
    def __init__(self, host, user, pswd, schm):
        self.host = host
        self.user = user
        self.pswd = pswd
        self.schm = schm

    def open(self):
        try:
            self.conn = MySQLdb.connect(host = self.host, user = self.user, passwd = self.pswd, db = self.schm)
            return True
        except:
            return False

    def close(self):
        autoutil.tryExcept(self.conn.close)

    def doSql(self, sql, *params):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            self.conn.commit()
            if sql.startswith('select'):
                return cursor.fetchall()
            elif sql.startswith('insert'):
                return cursor.lastrowid
        except:
            autoutil.tryExcept(self.conn.rollback)
        finally:
            autoutil.tryExcept(cursor.close)

#从uri中分离出host和location
def parseUrl(url):
    index1 = url.find('://') + 3
    proto = url[:index1 - 3]
    index2 = url.find('/', index1)
    if index2 == -1:
        return proto, url[index1:], '/'
    return proto, url[index1:index2], url[index2:]

#http请求,默认为get
def doHttp(url, headers = {}, method = 'GET', body = None):
    proto, host, location = parseUrl(url)
    baseHeaders = {}
    baseHeaders['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    baseHeaders['Accept-Charset'] = 'GBK,utf-8;q=0.7,*;q=0.3'
    if proto == 'http':
        baseHeaders['Accept-Encoding'] = 'gzip,deflate,sdch'
    baseHeaders['Accept-Language'] = 'zh-CN,zh;q=0.8'
    baseHeaders['Cache-Control'] = 'no-cache'
    baseHeaders['Connection'] = 'keep-alive'
    baseHeaders['Host'] = host
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
            autoutil.tryExcept(conn.close)

#http请求,post
def doHttpPost(url, body, headers = {}):
    return doHttp(url, headers, 'POST', body)
