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
        raise Exception('��ȡ����ϵͳ�汾ʧ��')

def getOSName():
    try:
        op = wmi.WMI().Win32_OperatingSystem()[0]        
        return op.Name
    except:
        raise Exception('��ȡ����ϵͳ����ʧ��')

def getOSPack():
    try:
        op = wmi.WMI().Win32_OperatingSystem()[0]        
        return op.ServicePackMajorVersion
    except:
        raise Exception('��ȡ����ϵͳSP�汾ʧ��')
    
def getIEVersion():
    import autoreg
    version = autoreg.getKeyValue(r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Internet Explorer','Version')
    if not version:
        raise Exception('��ȡIE�汾ʧ��')
    return version

def getIEPath():
    import autoreg
    IEPath = autoreg.getKeyValue(r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\IEXPLORE.EXE','')
    if not IEPath:
        raise Exception('��ȡIE·��ʧ��')
    return IEPath

def DisableUAC():
    cmd = r'reg ADD HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v ConsentPromptBehaviorAdmin /t REG_DWORD /d 0 /f >NUL 2>NUL'
    os.system(cmd)

#��ȡʱ���
def timestamp(style = '%Y-%m-%d %H:%M:%S'):
    return time.strftime(style, time.localtime())

def getCurrentTime():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

#���ڵĸ�ʽΪ��2011-09-09
#ʱ��ĸ�ʽΪ��05:05:05
def setCurrentTime(sDate=None,sTime=None):
    if sDate:
        os.system('date %s '%sDate)
    if sTime:
        os.system('time %s '%sTime)

#�ڵ�ǰ��ʱ������ϼ���������Ȼ��������ʱ��
def addTime(secAdded):
    timeString = time.strftime('%Y-%m-%d%H:%M:%S',time.localtime(time.time()+secAdded))
    sDate = timeString[0:10]
    sTime = timeString[10:]
    setCurrentTime(sDate,sTime)

def GetPhysMemorySize():
    return win32api.GlobalMemoryStatus()['TotalPhys']

#��ȡ��ǰ�û���Ϣ
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

#�жϵ�ǰ�û��Ƿ�����Domain
def isDomainUser():
    listUserInfo = getCurrentUserInfo()
    if listUserInfo[1] and len(listUserInfo[1]) > 0:
        return True
    return False