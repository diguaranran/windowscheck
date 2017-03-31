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

#��������
def createProcess(cmd, wait = False):
    proc = autoutil.tryExcept(subprocess.Popen, cmd)
    if autoutil.isExcept(proc):
        return
    if not wait:
        return proc.pid
    proc.wait()

#�ж�ָ��id�Ľ����Ƿ����
def existProcessId(pid):
    return existProcessIds([pid])

#�ж�ָ��id�Ľ����б��Ƿ����
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

#�ж�ָ��name�Ľ����Ƿ����
def existProcessName(pname):
    return existProcessNames([pname])

#�ж�ָ��name�Ľ����б��Ƿ����
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

#��ȡ�ӽ����б�
#rpidListΪ�Ѿ��ݹ���Ľ���id�б�
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

#��ȡ������id
def getParentProcessId(pid):
    rst, count = __execQuery__('select * from Win32_Process where ProcessId = %d' % pid)
    if count:
        return rst[0].ParentProcessId

#��ȡ���̵�GDI����
def getProcessGDI(pid):
    proc = autoutil.tryExcept(win32api.OpenProcess, win32con.PROCESS_ALL_ACCESS, 0, pid)
    if autoutil.isExcept(proc):
        return
    gdi = autoutil.tryExcept(win32process.GetGuiResources, proc.handle, win32con.GR_GDIOBJECTS)
    autoutil.tryExcept(proc.close)
    if not autoutil.isExcept(gdi):
        return gdi

#��ȡָ��name�Ľ���id
def getProcessIdByName(pname):
    rst, count = __execQuery__('select * from Win32_Process where Name = "%s"' % pname)
    if count:
        return rst[0].ProcessId

#��ȡָ��hwnd�Ľ���id
def getProcessIdByHwnd(hwnd):
    return win32process.GetWindowThreadProcessId(hwnd)[1]

#��ȡ����id�б�
def getProcessIds():
    rst, count = __execQuery__('select * from Win32_Process')
    pidList = []
    for i in range(count):
        pidList.append(rst[i].ProcessId)
    return pidList

#��ȡָ��id�Ľ���name
def getProcessNameById(pid):
    rst, count = __execQuery__('select * from Win32_Process where ProcessId = %d' % pid)
    if count:
        pname = autoutil.tryExcept(rst[0].Name.encode, sys.getfilesystemencoding())
        if not autoutil.isExcept(pname):
            return pname

#��ȡָ���û��Ľ���id�б�
def getUserProcessIds(user):
    rst, count = __execQuery__('select * from Win32_Process')
    pidList = []
    for i in range(count):
        owner = autoutil.tryExcept(rst[i].ExecMethod_, 'GetOwner')
        if not autoutil.isExcept(owner) and owner.User and owner.User.lower() == user.lower():
            pidList.append(rst[i].ProcessId)
    return pidList

#ɱ��ָ��id�Ľ���
def killProcessId(pid, user = None):
    killProcessIds([pid], user)

#ɱ��ָ��id�Ľ����б�
def killProcessIds(pidList, user = None):
    cmd = 'taskkill /F /T'
    if user:
        cmd += ' /FI "USERNAME eq %s"' % user
    for pid in pidList:
        cmd += ' /PID %d' % pid
    cmd += ' >NUL 2>NUL'
    os.system(cmd)

#ɱ��ָ��name�Ľ���
def killProcessName(pname, user = None):
    killProcessNames([pname], user)

#ɱ��ָ��name�Ľ����б�
def killProcessNames(pnameList, user = None):
    cmd = 'taskkill /F /T'
    if user:
        cmd += ' /FI "USERNAME eq %s"' % user
    for pname in pnameList:
        cmd += ' /IM %s' % pname
    cmd += ' >NUL 2>NUL'
    os.system(cmd)
