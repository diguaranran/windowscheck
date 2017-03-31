#coding:gbk

import autoutil
import copy
import os
import subprocess, sys
import win32api, win32con, win32process, wmi

def __execQuery__(sql):
    rst = wmi.WMI().ExecQuery(sql)
    count = autoutil.tryExcept(len, rst)
    if autoutil.isExcept(count):
        return __execQuery__(sql)
    return rst, count

#创建进程
def createProcess(cmd, wait = False):
    proc = autoutil.tryExcept(subprocess.Popen, cmd)
    if autoutil.isExcept(proc):
        return
    if not wait:
        return proc.pid
    proc.wait()

#判断指定id的进程是否存在
def existProcessId(pid):
    return existProcessIds([pid])

#判断指定id的进程列表是否存在
def existProcessIds(pidList, isAll = False):
    sql = 'select * from Win32_Process where ('
    for pid in pidList:
        if not sql.endswith('('):
            sql += ' or '
        sql += 'ProcessId = %d' % (pid,)
    sql += ')'
    count = __execQuery__(sql)[1]
    if isAll:
        return count == len(pidList)
    return count > 0

#判断指定name的进程是否存在
def existProcessName(pname):
    return existProcessNames([pname])

#判断指定name的进程列表是否存在
def existProcessNames(pnameList, isAll = False):
    sql = 'select * from Win32_Process where ('
    for pname in pnameList:
        if not sql.endswith('('):
            sql += ' or '
        sql += 'Name = "%s"' % (pname,)
    sql += ')'
    rst, count = __execQuery__(sql)
    if isAll:
        pnameSet = set()
        for i in range(count):
            pnameSet.add(rst[i].Name.encode(sys.getfilesystemencoding()))
        return len(pnameSet) == len(pnameList)
    return count > 0

#获取子进程列表
#rpidList为已经递归完的进程id列表
def getChildProcessIds(pid, rpidList = []):
    if pid in rpidList:
        return []
    rpidList = copy.copy(rpidList)
    rpidList.append(pid)
    rst, count = __execQuery__('select * from Win32_Process where ParentProcessId = %d' % pid)
    cpidSet = set()
    for i in range(count):
        if rst[i].ProcessId in rpidList:
            continue
        cpidSet.add(rst[i].ProcessId)
        cpidSet.update(getChildProcessIds(rst[i].ProcessId, rpidList))
    return list(cpidSet)

#获取父进程id
def getParentProcessId(pid):
    rst, count = __execQuery__('select * from Win32_Process where ProcessId = %d' % pid)
    if count:
        return rst[0].ParentProcessId

#获取进程的GDI数量
def getProcessGDI(pid):
    proc = autoutil.tryExcept(win32api.OpenProcess, win32con.PROCESS_ALL_ACCESS, 0, pid)
    if autoutil.isExcept(proc):
        return
    gdi = autoutil.tryExcept(win32process.GetGuiResources, proc.handle, win32con.GR_GDIOBJECTS)
    autoutil.tryExcept(proc.close)
    if not autoutil.isExcept(gdi):
        return gdi

#获取指定name的进程id
def getProcessIdByName(pname):
    rst, count = __execQuery__('select * from Win32_Process where Name = "%s"' % pname)
    if count:
        return rst[0].ProcessId

#获取指定hwnd的进程id
def getProcessIdByHwnd(hwnd):
    return win32process.GetWindowThreadProcessId(hwnd)[1]

#获取进程id列表
def getProcessIds():
    rst, count = __execQuery__('select * from Win32_Process')
    pidList = []
    for i in range(count):
        pidList.append(rst[i].ProcessId)
    return pidList

#获取指定id的进程name
def getProcessNameById(pid):
    rst, count = __execQuery__('select * from Win32_Process where ProcessId = %d' % pid)
    if count:
        pname = autoutil.tryExcept(rst[0].Name.encode, sys.getfilesystemencoding())
        if not autoutil.isExcept(pname):
            return pname

#获取指定用户的进程id列表
def getUserProcessIds(user):
    rst, count = __execQuery__('select * from Win32_Process')
    pidList = []
    for i in range(count):
        owner = autoutil.tryExcept(rst[i].ExecMethod_, 'GetOwner')
        if not autoutil.isExcept(owner) and owner.User and owner.User.lower() == user.lower():
            pidList.append(rst[i].ProcessId)
    return pidList

#杀掉指定id的进程
def killProcessId(pid, user = None):
    killProcessIds([pid], user)

#杀掉指定id的进程列表
def killProcessIds(pidList, user = None):
    cmd = 'taskkill /F /T'
    if user:
        cmd += ' /FI "USERNAME eq %s"' % user
    for pid in pidList:
        cmd += ' /PID %d' % pid
    cmd += ' >NUL 2>NUL'
    os.system(cmd)

#杀掉指定name的进程
def killProcessName(pname, user = None):
    killProcessNames([pname], user)

#杀掉指定name的进程列表
def killProcessNames(pnameList, user = None):
    cmd = 'taskkill /F /T'
    if user:
        cmd += ' /FI "USERNAME eq %s"' % user
    for pname in pnameList:
        cmd += ' /IM %s' % pname
    cmd += ' >NUL 2>NUL'
    os.system(cmd)
