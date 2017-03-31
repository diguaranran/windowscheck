#coding:gbk
import os,sys,wmi, win32api,time

def isWin64():
    ret = wmi.WMI().ExecQuery('select AddressWidth from Win32_Processor')
    if ret[0].AddressWidth == 32:
        return False
    elif ret[0].AddressWidth == 64:
        return True
    
def getOSVersion():
    try:
        op = wmi.WMI().Win32_OperatingSystem()[0]        
        return op.Version
    except:
        raise Exception('获取操作系统版本失败')

def getOSName():
    try:
        op = wmi.WMI().Win32_OperatingSystem()[0]        
        return op.Name
    except:
        raise Exception('获取操作系统名称失败')

def getOSPack():
    try:
        op = wmi.WMI().Win32_OperatingSystem()[0]        
        return op.ServicePackMajorVersion
    except:
        raise Exception('获取操作系统SP版本失败')
    
def getIEVersion():
    import autoreg
    version = autoreg.getKeyValue(r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Internet Explorer','Version')
    if not version:
        raise Exception('获取IE版本失败')
    return version

def getIEPath():
    import autoreg
    IEPath = autoreg.getKeyValue(r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\IEXPLORE.EXE','')
    if not IEPath:
        raise Exception('获取IE路径失败')
    return IEPath

def DisableUAC():
    cmd = r'reg ADD HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v ConsentPromptBehaviorAdmin /t REG_DWORD /d 0 /f >NUL 2>NUL'
    os.system(cmd)

#获取时间戳
def timestamp(style = '%Y-%m-%d %H:%M:%S'):
    return time.strftime(style, time.localtime())

def getCurrentTime():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

#日期的格式为：2011-09-09
#时间的格式为：05:05:05
def setCurrentTime(sDate=None,sTime=None):
    if sDate:
        os.system('date %s '%sDate)
    if sTime:
        os.system('time %s '%sTime)

#在当前的时间基础上加上秒数，然后再设置时间
def addTime(secAdded):
    timeString = time.strftime('%Y-%m-%d%H:%M:%S',time.localtime(time.time()+secAdded))
    sDate = timeString[0:10]
    sTime = timeString[10:]
    setCurrentTime(sDate,sTime)

def GetPhysMemorySize():
    return win32api.GlobalMemoryStatus()['TotalPhys']

#获取当前用户信息
#0---SID
#1---doman
#2---SID type
#3---username
def getCurrentUserInfo():
    listRet = []
    import win32security
    userName = win32api.GetUserName()
    userInfo = win32security.LookupAccountName(None,userName)
    listRet.append(userInfo[0])
    listRet.append(userInfo[1])
    listRet.append(userInfo[2])
    listRet.append(userName)
    return listRet

#判断当前用户是否属于Domain
def isDomainUser():
    listUserInfo = getCurrentUserInfo()
    if listUserInfo[1] and len(listUserInfo[1]) > 0:
        return True
    return False