#coding:GBK
import os,ctypes,time
import win32api,win32con,win32gui
import autocfg,autoutil

g_vMouseHandle = None
def __getMouDriver__():
    global g_vMouseHandle
    if not g_vMouseHandle:
        g_curFolder = os.path.dirname(win32api.GetFullPathName(__file__))
        g_curFolder = os.path.dirname(g_curFolder)
        mouDllPath = os.path.join(g_curFolder,'lib\\TrxdyDll.dll')
        if os.path.exists(mouDllPath):
            g_vMouseHandle = ctypes.windll.LoadLibrary(mouDllPath)
            g_vMouseHandle.Init()
    return g_vMouseHandle

#mode:
#    0---左键单击
#    1---右键单击
#    2---左键双击
#默认情况下，不使用驱动模式点击鼠标
def clickMouse(x, y, mode = autocfg.AU_CLICK_MOU_LEFT, byDriver = False):
    if byDriver:
        if not __getMouDriver__():
            return False
        __getMouDriver__().MoveTo(x,y)
        if mode == autocfg.AU_CLICK_MOU_LEFT:
            __getMouDriver__().LeftClick(1)
        elif mode == autocfg.AU_CLICK_MOU_RIGHT:
            __getMouDriver__().RightClick(1)
        elif mode == autocfg.AU_CLICK_MOU_DLEFT:
            __getMouDriver__().LeftDoubleClick(1)
        else:
            return False
    else:
        rect = win32gui.GetWindowRect(win32gui.GetDesktopWindow())
        x = int(float(x) / rect[2] * 65535)
        y = int(float(y) / rect[3] * 65535)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, x, y, 0, 0)        
        if mode == autocfg.AU_CLICK_MOU_LEFT:            
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)            
        elif mode == autocfg.AU_CLICK_MOU_RIGHT:            
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        elif mode == autocfg.AU_CLICK_MOU_DLEFT:
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        else:
            return False
    return True

#移动鼠标
#mode:0=消息模拟,1=驱动模拟
def moveMouse(x, y, byDriver = False):
    if byDriver:
        if not __getMouDriver__():
            return False
        __getMouDriver__().MoveTo(x,y)        
    else:
        rect = win32gui.GetWindowRect(win32gui.GetDesktopWindow())
        x = int(float(x) / rect[2] * 65535)
        y = int(float(y) / rect[3] * 65535)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, x, y, 0, 0)         
    return True

#模拟按键
def pressKeys(keyList):
    if type(keyList) == int:
        keyList = [keyList]
    elif type(keyList) == str:
        tmpKeyList = []
        for s in keyList:
            tmpKeyList.append(ord(s))
        keyList = tmpKeyList
    for key in keyList:
        win32api.keybd_event(key, 0, 0, 0)
    keyList.reverse()
    for key in keyList:
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

#模拟Alt+Tab
def pressAltTab():
    pressKeys([win32con.VK_MENU, win32con.VK_TAB])

if __name__ == '__main__':
    pressAltTab()

            