#coding:gbk
import os, time
from Lib import autoutil, autogui, autofile, autoproc, auto360
import Logger, htmlOutput

cLog = Logger.printLog()

def getTime():
    return time.strftime('%Y-%m-%d~%H_%M_%S', time.localtime())

def getWindowInfo():
    cfgFile = r'config\windowtime.ini'
    if not os.path.exists(cfgFile):
        cLog.Error('δ�ҵ������ļ�windowtime.ini��')
        return None
    try:
        iniDic = autofile.getIniDict(cfgFile)
    except:
        cLog.Error('ini��ʽ�������������ļ���')
        return None
    return iniDic

def recordResult(retDic):
    resFile = 'result[%s].html'%getTime()
    cLog.Comment('��������ļ�%s'%resFile)
    try:
        hResFile = open(resFile, 'w')
    except:
        cLog.Error('��������ļ�%sʧ��'%resFile)
        return None
    htmlOutput.writeHtmlHead(hResFile)
    htmlOutput.writeTableHead(hResFile)
    for exeName, timeList in retDic.items():
        total = 0
        count = 0
        for t in timeList:
            if t != -1:
                total += t
                count += 1
        aver = float(total) / float(count)
        htmlOutput.writeCheckItem(hResFile, exeName, timeList, aver)
    htmlOutput.writeTableTail(hResFile)
    htmlOutput.writeHtmlTail(hResFile)
    if hResFile:
        hResFile.close()
    return resFile

def main():
    retDic = {}
    cLog.Comment('��ȡexe�������кʹ�������')
    windowInfo = getWindowInfo()
    if not windowInfo:
        cLog.Error('��ȡexe�������кʹ�������ʧ��')
        return False
    for exeName, info in windowInfo.items():
        if autoproc.existProcessName(exeName):
            autoproc.killProcessName(exeName)
            autoutil.handleTimeout(autoutil.negative, 10, autoproc.existProcessName, exeName)
        if not info.has_key('cmd'):
            cLog.Error('%s: δ�ҵ�cmd����'%exeName)
            continue
        if not info.has_key('window'):
            cLog.Error('%s: δ�ҵ�window����'%exeName)
            continue
        cLog.Comment('����%s�������ܼ��'%exeName)
        retDic[exeName] = []
        cmd = os.path.join(auto360.getSafePath(), info['cmd'])
        for i in range(10):
            tBegin = time.time()
            autoproc.createProcess(cmd)
            if autoutil.handleTimeout(autogui.findWindow, 30, info['window']):
                tEnd = time.time()
                retDic[exeName].append(tEnd - tBegin)
                auto360.closeProtect()
                autoproc.killProcessName(exeName)
                autoutil.handleTimeout(autoutil.negative, 10, autoproc.existProcessName, exeName)
                time.sleep(0.5)
            else:
                cLog.Error('����%sδ�ҵ�'%info['window'])
                retDic[exeName].append(-1)
    resFile = recordResult(retDic)
    if resFile and os.path.exists(resFile):
        os.system(resFile)


if __name__ == '__main__':
    main()