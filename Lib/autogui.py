#coding:gbk

import autocfg, autoinput, autoproc, autoutil
import copy, ctypes
import re
import win32con, win32gui

#窗口基类
class BaseWindow:
    @staticmethod
    def parseClickConfig(clkCfg):
        if clkCfg == None:
            return None, None, autocfg.AU_CLICK_MOU_LEFT, False
        if type(clkCfg) == int:
            return None, None, clkCfg, False
        if type(clkCfg) == bool:
            return None, None, autocfg.AU_CLICK_MOU_LEFT, clkCfg
        if len(clkCfg) == 2:
            if type(clkCfg[0]) == int and type(clkCfg[1]) == int:
                return clkCfg[0], clkCfg[1], autocfg.AU_CLICK_MOU_LEFT, False
            return None, None, clkCfg[0], clkCfg[1]
        if len(clkCfg) == 3:
            if type(clkCfg[2]) == int:
                return clkCfg[0], clkCfg[1], clkCfg[2], False
            return clkCfg[0], clkCfg[1], autocfg.AU_CLICK_MOU_LEFT, clkCfg[2]
        return clkCfg

    @staticmethod
    def parseTitle(title):
        if type(title) == str:
            return title, None
        return title

    def __init__(self, hwnd):
        self.hwnd = hwnd

    #clkCfg:mode|useDrv|(x,y)|(mode,useDrv)|(x,y,mode)|(x,y,useDrv)|(x,y,mode,useDrv)
    def click(self, clkCfg = None):
        clickWindow(self.hwnd, clkCfg)

    #clkCfg:mode|useDrv|(x,y)|(mode,useDrv)|(x,y,mode)|(x,y,useDrv)|(x,y,mode,useDrv)
    def clickFor(self, timeout, cond, clkCfg = None):
        return clickWindowFor(self.hwnd, timeout, cond, clkCfg)

    #clkCfg:mode|useDrv|(x,y)|(mode,useDrv)|(x,y,mode)|(x,y,useDrv)|(x,y,mode,useDrv)
    def clickForClose(self, timeout, clkCfg = None):
        return clickWindowForClose(self.hwnd, timeout, clkCfg)

    #title:title|(title, parentTitle)
    #clkCfg:mode|useDrv|(x,y)|(mode,useDrv)|(x,y,mode)|(x,y,useDrv)|(x,y,mode,useDrv)
    def clickForFind(self, timeout, title, clkCfg = None):
        hwnd = clickWindowForFind(self.hwnd, timeout, title, clkCfg)
        if hwnd:
            return BaseWindow(hwnd)
        
    #timeout:timeout|(timeout,interval)
    #titleCfg:title|(title,isRaw)
    #clkCfg:mode|(x,y)|(x,y,mode)
    def clickForFindChild(self, timeout, titleCfg, clkCfg = None):
        hwnd = clickWindowForFindChild(self.hwnd, timeout, titleCfg, clkCfg)
        if hwnd:
            return BaseWindow(hwnd)        

    #clkCfg:mode|useDrv|(x,y)|(mode,useDrv)|(x,y,mode)|(x,y,useDrv)|(x,y,mode,useDrv)
    def clickForHidden(self, timeout, clkCfg = None):
        return clickWindowForHidden(self.hwnd, timeout, clkCfg)

    #clkCfg:mode|useDrv|(x,y)|(mode,useDrv)|(x,y,mode)|(x,y,useDrv)|(x,y,mode,useDrv)
    def clickForMd5(self, timeout, x, y, md5, clkCfg = None):
        return clickWindowForMd5(self.hwnd, timeout, x, y, md5, clkCfg)

    def getClass(self):
        return getWindowClass(self.hwnd)

    def getParent(self):
        return getParentWindow(self.hwnd)

    def getRect(self):
        return getWindowRect(self.hwnd)

    def getText(self):
        return getWindowText(self.hwnd)

    def find(self, title, isRaw = False):
        hwnd = findWindow(title, self.hwnd, isRaw)
        if hwnd:
            return BaseWindow(hwnd)

    def findTimeout(self, timeout, title, isRaw = False):
        return autoutil.handleTimeout(self.find, timeout, title, isRaw)

    def max(self):
        return maxWindow(self.hwnd)

    def min(self):
        return minWindow(self.hwnd)

    def setText(self, text):
        return setWindowText(self.hwnd, text)

    def show(self):
        return showWindow(self.hwnd)

    def top(self):
        return topWindow(self.hwnd)

#窗口类
class Window(BaseWindow):
    #title:title|(title, parentTitle)
    def __init__(self, timeout, title, cmd = None):
        title, parentTitle = BaseWindow.parseTitle(title)
        if not cmd:
            hwnd = autoutil.handleTimeout(findWindow, timeout, title, parentTitle)
            if not hwnd:
                raise Exception()
        hwnd = findWindow(title, parentTitle)
        if not hwnd:
            if not autoproc.createProcess(cmd):
                raise Exception()
            hwnd = autoutil.handleTimeout(findWindow, timeout, title, parentTitle)
            if not hwnd:
                raise Exception()
        BaseWindow.__init__(self, hwnd)

#点击窗口
#clkCfg:mode|useDrv|(x,y)|(mode,useDrv)|(x,y,mode)|(x,y,useDrv)|(x,y,mode,useDrv)
def clickWindow(hwnd, clkCfg = None):
    if isRawWindow(hwnd):
        return
    if not topWindow(hwnd):
        return
    rect = getWindowRect(hwnd)
    if not rect:
        return
    x, y, mode, useDrv = BaseWindow.parseClickConfig(clkCfg)
    if x == None:
        x = (rect[0] + rect[2]) / 2
    elif x < 0:
        x += rect[2]
    else:
        x += rect[0]
    if y == None:
        y = (rect[1] + rect[3]) / 2
    elif y < 0:
        y += rect[3]
    else:
        y += rect[1]
    autoinput.clickMouse(x, y, mode, useDrv)

#点击窗口等待条件满足
#clkCfg:mode|useDrv|(x,y)|(mode,useDrv)|(x,y,mode)|(x,y,useDrv)|(x,y,mode,useDrv)
def clickWindowFor(hwnd, timeout, cond, clkCfg = None):
    def __clickWindowFor__(hwnd, cond, clkCfg):
        rst = cond.do()
        if not rst or autoutil.isExcept(rst):
            clickWindow(hwnd, clkCfg)
        return rst
    return autoutil.handleTimeout(__clickWindowFor__, timeout, hwnd, cond, clkCfg)

#点击窗口等待窗口关闭
#clkCfg:mode|useDrv|(x,y)|(mode,useDrv)|(x,y,mode)|(x,y,useDrv)|(x,y,mode,useDrv)
def clickWindowForClose(hwnd, timeout, clkCfg = None):
    cond = autoutil.Condition(autoutil.negative, win32gui.IsWindow, hwnd)
    return clickWindowFor(hwnd, timeout, cond, clkCfg)

#点击窗口等待找到某窗口
#title:title|(title, parentTitle)
#clkCfg:mode|useDrv|(x,y)|(mode,useDrv)|(x,y,mode)|(x,y,useDrv)|(x,y,mode,useDrv)
def clickWindowForFind(hwnd, timeout, title, clkCfg = None):
    title, parentTitle = BaseWindow.parseTitle(title)
    cond = autoutil.Condition(findWindow, title, parentTitle)
    return clickWindowFor(hwnd, timeout, cond, clkCfg)

#点击窗口等待窗口不可见
#clkCfg:mode|useDrv|(x,y)|(mode,useDrv)|(x,y,mode)|(x,y,useDrv)|(x,y,mode,useDrv)
def clickWindowForHidden(hwnd, timeout, clkCfg = None):
    cond = autoutil.Condition(autoutil.negative, win32gui.IsWindowVisible, hwnd)
    return clickWindowFor(hwnd, timeout, cond, clkCfg)

#点击窗口等待找到该窗口的某子窗口
#timeout:timeout|(timeout,interval)
#titleCfg:title|(title,isRaw)
#clkCfg:mode|(x,y)|(x,y,mode)
def clickWindowForFindChild(hwnd, timeout, titleCfg, clkCfg = None):
    if type(titleCfg) == tuple:
        titleCfg = titleCfg[0], hwnd, titleCfg[1]
    else:
        titleCfg = titleCfg, hwnd
    return clickWindowForFind(hwnd, timeout, titleCfg, clkCfg)

#点击窗口等待某区域像素的md5匹配
#clkCfg:mode|useDrv|(x,y)|(mode,useDrv)|(x,y,mode)|(x,y,useDrv)|(x,y,mode,useDrv)
def clickWindowForMd5(hwnd, timeout, x, y, md5, clkCfg = None):
    def __clickWindowForMd5__(hwnd, x, y, md5):
        if not topWindow(hwnd):
            return False
        rect = getWindowRect(hwnd)
        if not rect:
            return False
        if x < 0:
            x += rect[2]
        else:
            x += rect[0]
        if y < 0:
            y += rect[3]
        else:
            y += rect[1]
        return autoutil.md5Grab((x - 5, y - 5, x + 6, y + 6)) == md5
    cond = autoutil.Condition(__clickWindowForMd5__, hwnd, x, y, md5)
    return clickWindowFor(hwnd, timeout, cond, clkCfg)

#查找第一个窗口（包含不可见、不可用、阻塞）
#title:text,class,ctrlid
#parentTitle:None,hwnd,text,class
def findRawWindow(title, parentTitle = None):
    return findWindow(title, parentTitle, True)

#查找窗口（包含不可见、不可用、阻塞）
#title:text,class,ctrlid
#parentTitle:None,hwnd,text,class
def findRawWindows(title, parentTitle = None):
    return findWindows(title, parentTitle, True)

#查找第一个窗口
#title:text,class,ctrlid
#parentTitle:None,hwnd,text,class
def findWindow(title, parentTitle = None, isRaw = False):
    hwndList = findWindows(title, parentTitle, isRaw)
    if hwndList:
        return hwndList[0]

#查找窗口
#title:text,class,ctrlid
#parentTitle:None,hwnd,text,class
def findWindows(title, parentTitle = None, isRaw = False):
    def __fillWindowAttrs__(hwnd, wnds):
        text = re.split('[\r|\n]+', getWindowText(hwnd))[0].strip()
        clazz = getWindowClass(hwnd).strip()
        ctrlId = win32gui.GetDlgCtrlID(hwnd)
        wnds[hwnd] = text, clazz, ctrlId
    def __enumChildWindows__(hwnd, hwnds):
        hwnds.add(hwnd)
        cwnds = {}
        if not hwnd:
            autoutil.tryExcept(win32gui.EnumWindows, __fillWindowAttrs__, cwnds)
        else:
            autoutil.tryExcept(win32gui.EnumChildWindows, hwnd, __fillWindowAttrs__, cwnds)
            for hcwnd in cwnds.keys():
                if hcwnd not in hwnds:
                    cwnds.update(__enumChildWindows__(hcwnd, hwnds))
        return cwnds
    def __findChildWindows__(hwnd, hwnds):
        hwnds.add(hwnd)
        cwnds = {}
        hcwnd = autoutil.tryExcept(win32gui.FindWindowEx, hwnd, None, None, None)
        while hcwnd and not autoutil.isExcept(hcwnd) and hcwnd not in hwnds:
            __fillWindowAttrs__(hcwnd, cwnds)
            if hwnd:
                cwnds.update(__findChildWindows__(hcwnd, hwnds))
            hcwnd = autoutil.tryExcept(win32gui.FindWindowEx, hwnd, hcwnd, None, None)
        return cwnds
    def __getChildWindows__(hwnd, hwnds):
        hwnds.add(hwnd)
        cwnds = {}
        hcwnd = autoutil.tryExcept(win32gui.GetWindow, hwnd or win32gui.GetDesktopWindow(), win32con.GW_CHILD)
        while hcwnd and not autoutil.isExcept(hcwnd) and hcwnd not in hwnds:
            __fillWindowAttrs__(hcwnd, cwnds)
            if hwnd:
                cwnds.update(__getChildWindows__(hcwnd, hwnds))
            hcwnd = autoutil.tryExcept(win32gui.GetWindow, hcwnd, win32con.GW_HWNDNEXT)
        return cwnds
    def __matchWindows__(wnds, title):
        hwnds = []
        for hwnd in wnds:
            text, clazz, ctrlId = wnds[hwnd]
            if type(title) == int:
                if ctrlId == title:
                    hwnds.append(hwnd)
            elif text == title or re.match('^' + title + '$', text, re.S) or clazz == title or re.match('^' + title + '$', clazz, re.S):
                if isRaw or not isRawWindow(hwnd):
                    hwnds.append(hwnd)
        return hwnds
    if not parentTitle:
        hpwndList = [None]
    elif type(parentTitle) == int:
        hpwndList = [parentTitle]
    else:
        hpwndList = findRawWindows(parentTitle)
    wnds = {}
    hwnds = set()
    for hpwnd in hpwndList:
        hwnds.clear()
        wnds.update(__enumChildWindows__(hpwnd, hwnds))
        hwnds.clear()
        wnds.update(__findChildWindows__(hpwnd, hwnds))
        hwnds.clear()
        wnds.update(__getChildWindows__(hpwnd, hwnds))
    return __matchWindows__(wnds, title)

def getParentWindow(hwnd):
    hwnd = autoutil.tryExcept(win32gui.GetParent, hwnd)
    if not autoutil.isExcept(hwnd):
        return hwnd

#获取窗口类名
def getWindowClass(hwnd, buf = ctypes.c_buffer(1024)):
    size = ctypes.sizeof(buf)
    ctypes.memset(buf, 0, size)
    ctypes.windll.user32.GetClassNameA(hwnd, ctypes.addressof(buf), size)
    return buf.value.strip()

#获得窗口尺寸
def getWindowRect(hwnd):
    rect = autoutil.tryExcept(win32gui.GetWindowRect, hwnd)
    if not autoutil.isExcept(rect):
        return rect

#获取窗口文字
def getWindowText(hwnd, buf = ctypes.c_buffer(1024)):
    text = win32gui.GetWindowText(hwnd).strip()
    if not text:
        size = ctypes.sizeof(buf)
        ctypes.memset(buf, 0, size)
        autoutil.tryExcept(win32gui.SendMessageTimeout, hwnd, win32con.WM_GETTEXT, size, buf, win32con.SMTO_ABORTIFHUNG, 30)
        text = buf.value.strip()
    return text

#判断是否为非正常窗口
def isRawWindow(hwnd):
    return not win32gui.IsWindowVisible(hwnd) or not win32gui.IsWindowEnabled(hwnd) or ctypes.windll.user32.IsHungAppWindow(hwnd)

#最大化窗口
def maxWindow(hwnd):
    return showWindow(hwnd, win32con.SW_SHOWMAXIMIZED)

#最小化窗口
def minWindow(hwnd):
    return showWindow(hwnd, win32con.SW_SHOWMINIMIZED)

#设置窗口文字
def setWindowText(hwnd, text):
    rst = autoutil.tryExcept(win32gui.SendMessageTimeout, hwnd, win32con.WM_SETTEXT, 0, text, win32con.SMTO_ABORTIFHUNG, 30)
    return not autoutil.isExcept(rst)

#显示窗口
def showWindow(hwnd, showType = win32con.SW_SHOWDEFAULT):
    return win32gui.ShowWindow(hwnd, showType)

#置顶窗口
def topWindow(hwnd):
    hwndList = [hwnd]
    while True:
        hwnd = getParentWindow(hwnd)
        if not hwnd:
            break
        hwndList.append(hwnd)
    topHwnd = None
    while len(hwndList) > 0:
        hwnd = hwndList.pop()
        if not isRawWindow(hwnd):
            topHwnd = hwnd
            break
    if not topHwnd:
        return False
    wl = win32gui.GetWindowLong(topHwnd, win32con.GWL_EXSTYLE)
    if int(hex(wl)[-1]) == win32con.WS_EX_TOPMOST:
        return True
    autoutil.tryExcept(win32gui.SetWindowPos, topHwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE|win32con.SWP_NOSIZE)
    return True

#通过ID得到子窗口句柄
def GetHwndById(hParent, id):
    if not hParent:
        return None
    hwndChild = None
    try:
        hwndChild = win32gui.GetDlgItem(hParent,id)
    except:
        return None
    if not hwndChild:
        return None
    return hwndChild
