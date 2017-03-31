#coding:gbk

import autogui, autoproc, autoreg, autosys, autoutil
import os
import win32con

class SafeMainWindow(autogui.Window):
    def __init__(self):
        safePath = getSafePath()
        if not safePath:
            raise Exception()
        autogui.Window.__init__(self, 20, 'Q360SafeMainClass', r'%s\360Safe.exe' % safePath)

    def close(self):
        return self.clickForClose(3, (-30, 10))

    def repairSystem(self):
        wndObj1 = self.clickForFind(3, (0x457, self.hwnd), (336, 52))
        if not wndObj1:
            return False
        wndObj2 = wndObj1.clickForFind(60, (0x45d, self.hwnd))
        if not wndObj2:
            return False
        return wndObj2.clickForHidden(3)
        #type:  1--返回垃圾清理窗口对象
    #       2--返回痕迹清理窗口对象
    def computeClean(self,cleanType):
        self.clickTabButton(5)
        winobj = None
        y = 130
        if cleanType == 1:
            x = 160
            winobj = self.clickForFind(3,('360TrashCleanTab',self.hwnd),(x,y))
        else:
            x = 270
            winobj = self.clickForFind(3,('AUTO_TEST1',self.hwnd),(x,y))
        if winobj:
            return winobj
        return None    
        
    def clickTabButton(self,index):
        xy = None
        x = 35 + index*73
        y = 70
        wndObj1 = self.click((x,y)) 

#获取卫士安装路径
def getSafePath():
    if autosys.isWin64():
        return autoreg.getKeyValue(r'HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\App Paths\360safe.exe', 'Path')
    return autoreg.getKeyValue(r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\360safe.exe', 'Path')

SAFE_PATH = getSafePath()

#关闭自我保护
def closeProtect():
    safePath = getSafePath()
    if not safePath:
        return
    def __closeProtect__(flag):
        if flag.get():
            return True
        hwnd = autogui.findWindow('是|确定', '360(产品|安全卫士)')
        if not hwnd:
            return False
        parentHwnd = autogui.getParentWindow(hwnd)
        if not parentHwnd:
            return False
        if not autogui.maxWindow(parentHwnd):
            return False
        autogui.clickWindow(hwnd)
        return False
    flag = autoutil.Data(False)
    autoutil.doInThread(autoutil.handleTimeout, __closeProtect__, 30, flag)
    autoproc.createProcess(r'%s\safemon\360tray.exe /disablesp 1' % safePath, True)
    flag.set(True)

#开启自我保护
def openProtect():
    safePath = getSafePath()
    if not safePath:
        return
    autoproc.createProcess(r'%s\safemon\360tray.exe /disablesp 0' % safePath, True)

#关闭主动防御
def closeZDFY():
    autoproc.killProcessNames('zhudongfangyu.exe')

#开启主动防御
def openZDFY():
    os.system('net start zhudongfangyu >NUL 2>NUL')

#获取弹出窗口颜色
def getColor(hwnd, threshold = 3):
    rect = autogui.getWindowRect(hwnd)
    if not rect:
        return
    im = autoutil.grabImage((rect[0], rect[1], rect[0] + 1, rect[1] + 50))
    for y in range(50):
        r, g, b = im.getpixel((0, y))
        if abs(r - 44) <= threshold and abs(g - 98) <= threshold and abs(b - 21) <= threshold:
            return 'green'
        if abs(r - 139) <= threshold and abs(g - 87) <= threshold and abs(b - 22) <= threshold:
            return 'orange'
        if abs(r - 91) <= threshold and abs(g - 18) <= threshold and abs(b - 5) <= threshold:
            return 'red'
        if abs(r - 118) <= threshold and abs(g - 141) <= threshold and abs(b - 155) <= threshold:
            return 'blue'

#关闭卫士自动升级
def closeSafeUpdate():
    if autosys.isWin64():
        keyPath = r'HKLM\SOFTWARE\Wow6432Node\360Safe\setting'
    else:
        keyPath = r'HKLM\SOFTWARE\360Safe\setting'    
    autoreg.setKeyValue(keyPath, 'update', win32con.REG_DWORD, '3')
    autoreg.setKeyValue(keyPath, 'ForceUpdateLibs', win32con.REG_DWORD, '0')   
