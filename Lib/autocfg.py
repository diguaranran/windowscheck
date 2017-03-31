#coding:GBK
import os
import ctypes
import win32api
from win32com.shell import shell
from win32com.shell import shellcon

AU_CLICK_MOU_LEFT = 0
AU_CLICK_MOU_RIGHT = 1
AU_CLICK_MOU_DLEFT = 2

GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
VirtualAllocEx = ctypes.windll.kernel32.VirtualAllocEx
VirtualFreeEx = ctypes.windll.kernel32.VirtualFreeEx
OpenProcess = ctypes.windll.kernel32.OpenProcess
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory
GetMenuItemCount = ctypes.windll.user32.GetMenuItemCount
GetMenuItemRect = ctypes.windll.user32.GetMenuItemRect


def __get_special_path(ptype):        
    idList = shell.SHGetSpecialFolderLocation(0, ptype)
    return shell.SHGetPathFromIDList(idList)

def __getPath__(path, fileName = None):    
    if fileName:        
        fileName = os.path.basename(fileName)
        return os.path.join(path, fileName)
    return path

def GetCookiesPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_COOKIES), fileName)

def GetLocalApp(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_LOCAL_APPDATA), fileName)

def GetTempPath(fileName=None):
    if fileName:
        return os.path.join(win32api.GetLongPathName(os.environ['TMP']), fileName)
    else:
        return win32api.GetLongPathName(os.environ['TMP'])
    
def GetWindowsTempPath(fileName=None):
    if fileName:return os.path.join(win32api.GetLongPathName(os.environ['SYSTEMROOT']), 'Temp', fileName)
    else:return os.path.join(win32api.GetLongPathName(os.environ['SYSTEMROOT']), 'Temp')

def GetPublicPath(fileName = None):
    publicPath = os.path.join(os.environ['HOMEDRIVE'], r'Users\Public')
    if fileName:
        return os.path.join(publicPath, fileName)
    else:
        return publicPath
    
def GetCommonApp(fileName=None):
    return __getPath__(__get_special_path(shellcon.CSIDL_COMMON_APPDATA), fileName)

def GetCommonPrograms(fileName=None):
    return __getPath__(__get_special_path(shellcon.CSIDL_COMMON_PROGRAMS), fileName)
    
def GetDesktopPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_DESKTOP), fileName)

def GetStartMenuPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_STARTMENU), fileName)

def GetCommonStartMenuPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_COMMON_STARTMENU), fileName)

def GetFavoritePath(fileName = None):    
    return __getPath__(__get_special_path(shellcon.CSIDL_FAVORITES), fileName)

def GetPersonalPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_PERSONAL), fileName)

def GetProfilePath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_PROFILE), fileName)

def GetLocalLowPath(fileName = None):
    if fileName:
        return os.path.join(GetProfilePath(), 'AppData\LocalLow', fileName)
    else:
        return os.path.join(GetProfilePath(), 'AppData\LocalLow')

def GetDesktopDirectoryPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_DESKTOPDIRECTORY), fileName)

def GetCommonDesktopDirectoryPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_COMMON_DESKTOPDIRECTORY), fileName)

def GetFontsPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_FONTS), fileName)

def GetProGramsPath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_PROGRAMS), fileName)

def GetAppData(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_APPDATA), fileName)
def GetInternetCachePath(fileName = None):
    return __getPath__(__get_special_path(shellcon.CSIDL_INTERNET_CACHE), fileName)
def GetQuickLaunchPath(fileName = None):
    path = os.path.join(GetAppData(),'Microsoft\Internet Explorer\Quick Launch')    
    if fileName:
        fileName = os.path.basename(fileName)
        return os.path.join(path, fileName)
    return path

extEnviron = os.environ
if not extEnviron.has_key('PUBLIC'):
    extEnviron['PUBLIC'] = GetPublicPath()
if not extEnviron.has_key('DESKTOPDIRECTORY'):
    extEnviron['DESKTOPDIRECTORY'] = GetDesktopDirectoryPath()
if not extEnviron.has_key('COMMON_DESKTOPDIRECTORY'):
    extEnviron['COMMON_DESKTOPDIRECTORY'] = GetCommonDesktopDirectoryPath()
if not extEnviron.has_key('INTERNET_CACHE'):
    extEnviron['INTERNET_CACHE'] = GetInternetCachePath()
if not extEnviron.has_key('WINDOWS'):
    extEnviron['WINDOWS'] = extEnviron['SYSTEMROOT']
if not extEnviron.has_key('SYSTEM'):
    extEnviron['SYSTEM'] = os.path.join(extEnviron['SYSTEMROOT'], 'system32')
if not extEnviron.has_key('DESKTOP'):
    extEnviron['DESKTOP'] = GetDesktopPath()
if not extEnviron.has_key('STARTMENU'):
    extEnviron['STARTMENU'] = GetStartMenuPath()
if not extEnviron.has_key('COMMON_STARTMENU'):
    extEnviron['COMMON_STARTMENU'] = GetCommonStartMenuPath()
if not extEnviron.has_key('FAVORITES'):
    extEnviron['FAVORITES'] = GetFavoritePath()
if not extEnviron.has_key('PERSONAL'):
    extEnviron['PERSONAL']  = GetPersonalPath()
if not extEnviron.has_key('FONTS'):
    extEnviron['FONTS']     = GetFontsPath()
if not extEnviron.has_key('PROGRAMS'):
    extEnviron['PROGRAMS']  = GetProGramsPath()
if not extEnviron.has_key('QUICKLAUNCH'):
    extEnviron['QUICKLAUNCH']  = GetQuickLaunchPath()
if not extEnviron.has_key('REPAIRBAK'):
    extEnviron['REPAIRBAK'] = r'%appdata%\repairbak'
if not extEnviron.has_key('COMMON_APPDATA'):
    extEnviron['COMMON_APPDATA'] = GetCommonApp()
if not extEnviron.has_key('LOCAL_APPDATA'):
    extEnviron['LOCAL_APPDATA'] = GetLocalApp()
if not extEnviron.has_key('TEMP'):
    extEnviron['TEMP'] = GetTempPath()
if not extEnviron.has_key('WINDOWSTEMP'):
    extEnviron['WINDOWSTEMP'] = GetWindowsTempPath()
if not extEnviron.has_key('COOKIES'):
    extEnviron['COOKIES'] = GetCookiesPath()
if not extEnviron.has_key('PROFILE'):
    extEnviron['PROFILE'] = GetProfilePath()
if not extEnviron.has_key('LOCALLOWAPPDATA'):
    extEnviron['LOCALLOWAPPDATA'] = GetLocalLowPath()
if not extEnviron.has_key('COMMON_PROGRAMS'):
    extEnviron['COMMON_PROGRAMS'] = GetCommonPrograms()