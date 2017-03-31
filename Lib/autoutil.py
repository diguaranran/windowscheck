#coding:gbk

import hashlib
import ImageGrab
import logging
import MySQLdb
import random
import threading, time
import pythoncom
import subprocess

#数据对象
class Data:
    def __init__(self, data = None):
        self.data = data

    def get(self):
        return self.data

    def set(self, data):
        self.data = data

#条件对象
class Condition:
    def __init__(self, func, *params, **paramMap):
        self.func = func
        self.params = params
        self.paramMap = paramMap

    def do(self):
        return self.func(*self.params, **self.paramMap)

#数据库连接对象
class DBAccessor:
    def __init__(self, host, user, pswd, schm):
        self.host = host
        self.user = user
        self.pswd = pswd
        self.schm = schm
        self.conn = None

    def do(self, sql, *params):
        if self.conn and isExcept(tryExcept(self.conn.stat)):
            self.close()
        if not self.conn:
            conn = tryExcept(MySQLdb.connect, host = self.host, user = self.user, passwd = self.pswd, db = self.schm)
            if isExcept(conn):
                return conn
            self.conn = conn
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)
            try:
                if sql.startswith('select'):
                    return cursor.fetchall()
                elif sql.startswith('insert'):
                    return cursor.lastrowid
            finally:
                cursor.close()
                self.conn.commit()
        except Exception, e:
            tryExcept(self.conn.rollback)
            return e

    def close(self):
        if self.conn:
            tryExcept(self.conn.close)
            self.conn = None

#函数线程
class FuncThread(threading.Thread):
    def __init__(self, func, *params, **paramMap):
        threading.Thread.__init__(self)
        self.func = func
        self.params = params
        self.paramMap = paramMap
        self.rst = None
        self.finished = False
        self.flag = True

    def run(self):
        pythoncom.CoInitialize()
        try:
            self.rst = self.func(*self.params, **self.paramMap)
        except:
            self.flag = False
        self.finished = True
        pythoncom.CoUninitialize()

    def getResult(self):
        return self.rst

    def isFinished(self):
        return self.finished

#获取某区域指定像素的数量
#rgb:(r,g,b)
def countPixels(rect, rgb):
    img = grabImage(rect)
    w, h = rect[2] - rect[0], rect[3] - rect[1]
    num = 0
    for i in range(w):
        for j in range(h):
            if img.getpixel((i, j)) == rgb:
                num += 1
    return num

#在线程中执行
def doInThread(func, *params, **paramMap):
    ft = FuncThread(func, *params, **paramMap)
    ft.start()
    return ft

#获取日志对象
def getLogger(path, level):
    logger = logging.getLogger(path)
    logger.setLevel(level)
    fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    fh = logging.FileHandler(path)
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger

#获取某区域的截图
def grabImage(rect, filename = None):
    img = ImageGrab.grab(rect)
    if filename:
        img.save(filename)
    return img

#判断指定位置是否与像素匹配
#rgb:(r,g,b)
def matchPixel(x, y, rgb):
    return getPixel(x, y) == rgb

#获取指定位置像素
def getPixel(x, y):
    img = grabImage((x, y, x + 1, y+1))
    return img.getpixel((0, 0))

#在超时范围内执行
#timeout为数值或元组（超时时长,间隔时间）
def handleTimeout(func, timeout, *params, **paramMap):
    interval = 0.3
    if type(timeout) == tuple:
        timeout, interval = timeout
    while timeout > 0:
        t = time.time()
        rst = func(*params, **paramMap)
        if rst and not isExcept(rst):
            break
        time.sleep(interval)
        timeout -= time.time() - t
    return rst

#判断是否为异常
def isExcept(e, eType = Exception):
    return isinstance(e, eType)

#计算md5
def md5(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()

#计算文件md5
def md5File(path, size = 32768):
    m = hashlib.md5()
    f = open(path, 'rb')
    while True:
        d = f.read(size)
        if not d:
            break
        m.update(d)
    f.close()
    return m.hexdigest()

#计算截图的md5
def md5Image(rect):
    img = grabImage(rect)
    return md5(img.tostring())

#取反执行
def negative(func, *params, **paramMap):
    return not func(*params, **paramMap)

#获取随机数字串
def randomIntStr():
    return str(random.random())[2:]

#获取时间戳
def timestamp(style = '%Y-%m-%d %H:%M:%S'):
    return time.strftime(style, time.localtime())

#在try中执行
def tryExcept(func, *params, **paramMap):
    try:
        return func(*params, **paramMap)
    except Exception, e:
        return e

def spawn(command, isobs=True):
    #阻塞模式
    try:
        pipe = subprocess.Popen(command+" 2>&1",shell=True,stdout=subprocess.PIPE)
        if isobs:
            pipe.communicate()
        return True
    except:
        pass
    return False
