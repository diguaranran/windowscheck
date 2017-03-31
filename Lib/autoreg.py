#coding:GBK
#------注册表操作------
import os,sys,ctypes,win32con,winnt,win32api
import autosys

REG_SZ = win32con.REG_SZ
REG_DWORD = win32con.REG_DWORD
REG_MULTI_SZ = win32con.REG_MULTI_SZ
REG_EXPAND_SZ = win32con.REG_EXPAND_SZ

g_qaCommonDriver = None #注册表驱动句柄
g_qaOS64Bit = False

if autosys.isWin64():g_qaOS64Bit = True

def getSamDesired(attr,reDirect=False):
    samDesired = attr    
    if g_qaOS64Bit and reDirect:
        samDesired = attr|win32con.KEY_WOW64_64KEY
    return samDesired

def _get_cur_file_dir():
    #获取脚本路径
    path = sys.path[0]
    #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)
    
def __getQADriver__():
    global g_qaCommonDriver 
    if not g_qaCommonDriver :
        curFolder = _get_cur_file_dir()
        dllPath = os.path.join(curFolder,'QACommon_Dll.dll')
        if not os.path.exists(dllPath):
            dllPath = os.path.join(curFolder,'lib\\QACommon_Dll.dll')
        if os.path.exists(dllPath):
            g_qaCommonDriver  = ctypes.windll.LoadLibrary(dllPath)
            g_qaCommonDriver .Init()
    return g_qaCommonDriver 
    
def EndQACommonDriver():
    global g_qaCommonDriver
    if g_qaCommonDriver:
        g_qaCommonDriver.End()
        g_qaCommonDriver = None
        

#返回注册表键是否存在
#参数:
#   keyFullName: 键全名
#存在返回True，否则返回False
def hasKey(keyFullName, reDirect= False,byDriver = False):
    if byDriver:
        if __getQADriver__():
            return __getQADriver__().KeyExistsEx(keyFullName,reDirect)    
    else:
        #使用ring3层逻辑判断是否存在
        hreg = None
        rootKeyName, subKeyName = _getRootAndSub(keyFullName)
        try:
            hreg = win32api.RegOpenKeyEx(rootKeyName, subKeyName, 0, getSamDesired(win32con.KEY_READ,reDirect))
        except Exception,e:
            return False
        finally:
            if hreg:
                win32api.RegCloseKey(hreg)
        return True

def __getRegSubKeysList__(keyFullName, subKeys, reDirect=False):
    rootKeyName, subKeyName = _getRootAndSub(keyFullName)
    try:
        hreg = win32api.RegOpenKeyEx(rootKeyName, subKeyName, 0, getSamDesired(win32con.KEY_READ,reDirect))
    except:
        return False
    finally:
        if hreg:
            win32api.RegCloseKey(hreg)
    if hreg:        
        subKeyTuple = win32api.RegEnumKeyEx(hreg)
        win32api.RegCloseKey(hreg)
        if subKeyTuple:
            for subKey in subKeyTuple:
                subKeyPath = keyFullName + '\\' + subKey[0]
                subKeys.insert(0, subKeyPath)
                __getRegSubKeysList__(subKeyPath, subKeys)
            
#删除注册表中的某键
#参数:
#   keyFullName: 键全名
#此操作会删除键级键的所有子键
def delKey(keyFullName, reDirect=False,byDriver = False):
    if byDriver:
        if hasKey(keyFullName, byDriver):
            return __getQADriver__().DelKeyEx(keyFullName,reDirect)
    else:
        if hasKey(keyFullName,reDirect):
            subKeysList = []
            __getRegSubKeysList__(keyFullName, subKeysList)
            subKeysList.append(keyFullName)
            for subKey in subKeysList:
                rootKeyName, subKeyName = _getRootAndSub(subKey)
                try:
                    if g_qaOS64Bit:
                        win32api.RegDeleteKeyEx(rootKeyName, subKeyName,getSamDesired(win32con.KEY_WRITE,reDirect),0)
                    else:
                        win32api.RegDeleteKey(rootKeyName, subKeyName)
                except Exception,e:
                    return False
            return True
    return True

#向注册表中添加键
def addKey(keyFullName, reDirect=False,byDriver = False):
    bRet = True
    bExist = False
    if byDriver:
        bExist = hasKey(keyFullName, reDirect,byDriver)
        if not bExist:
            bRet = __getQADriver__().AddKeyEx(keyFullName,reDirect)                           
        return bRet
    else:
        bExist = hasKey(keyFullName,reDirect)
        if not bExist:
            hreg = None
            flag = 0
            rootKeyName, subKeyName = _getRootAndSub(keyFullName)
            try:
                hreg, flag =  win32api.RegCreateKeyEx(rootKeyName, subKeyName, getSamDesired(win32con.KEY_WRITE,reDirect), None, winnt.REG_OPTION_NON_VOLATILE, None, None)
            except:
                return False
            finally:
                if hreg:
                    win32api.RegCloseKey(hreg)
        return True
            

#获取注册表键的值
#参数:
#   keyFullName: 键全名
#   valueName: 值名（可选，为None时返回键的默认值）
#当键不存在时，返回None
def getKeyValue(keyFullName, valueName = None,buf = ctypes.c_buffer(512), reDirect=False,byDriver = False):
    if byDriver:
        if hasKey(keyFullName,reDirect, byDriver):
            ctypes.memset(buf, 0, 512)
            ret = __getQADriver__().GetKeyValueEx(keyFullName,valueName,buf,reDirect)
            if not ret:
                return None
            return buf.value
    else:
        if hasKey(keyFullName,reDirect):
            hreg = None
            valueData = ''
            rootKeyName, subKeyName = _getRootAndSub(keyFullName)
            try:
                hreg = win32api.RegOpenKeyEx(rootKeyName, subKeyName, 0, getSamDesired(win32con.KEY_READ,reDirect))
                valueData, REG_type = win32api.RegQueryValueEx(hreg, valueName)
                if REG_type == win32con.REG_DWORD and valueData < 0:
                    ctypes.memset(buf, 0, 512)
                    ret = __getQADriver__().GetKeyValueEx(keyFullName,valueName,buf,reDirect)
                    if not ret:
                        return None
                    return buf.value
                return str(valueData)
            except Exception, e:
                return None
            finally:
                if hreg:
                    win32api.RegCloseKey(hreg)
    return None

def getKeyValue2(keyFullName, valueName = None,regType = ctypes.c_uint(),buf = ctypes.c_buffer(512),ccbLen = ctypes.c_uint(),reDirect=False,byDriver = False):
    if byDriver:
        if hasKey(keyFullName, reDirect,byDriver):
            retString = ''
            ctypes.memset(buf, 0, 512)
            ret = __getQADriver__().GetKeyValueEx2(keyFullName,valueName,ctypes.addressof(regType),buf,ctypes.addressof(ccbLen),reDirect)
            if not ret:            
                return None
            if REG_MULTI_SZ == regType.value:
                return buf[0:ccbLen.value].split(chr(0))[0:-2]
            else:
                return (regType.value,buf.value,ccbLen.value)
    else:
        pass
    return None

def hasKeyValue(keyFullName, valueName,reDirect = False,byDriver = False):
    if byDriver:
        if getKeyValue(keyFullName, valueName, ctypes.c_buffer(512), reDirect,byDriver) == None:
            return False
        else:
            return True
    else:
        if getKeyValue(keyFullName, valueName,ctypes.c_buffer(512),reDirect) == None:
            return False
        else:
            return True

#设置注册表键的值
#参数:
#   keyFullName: 键全名
#   valueName: 值名
#   type: 值类型
#   value: 值
def setKeyValue(keyFullName, valueName, type, value, reDirect=False,byDriver = False):
    if byDriver:
        return __getQADriver__().SetKeyValueEx(keyFullName,type,valueName,value,reDirect)
    else:
        hreg = None
        if not hasKey(keyFullName,reDirect):
            addKey(keyFullName)
        rootKeyName, subKeyName = _getRootAndSub(keyFullName)
        try:
            hreg = win32api.RegOpenKeyEx(rootKeyName, subKeyName, 0, getSamDesired(win32con.KEY_WRITE,reDirect))
            if type == win32con.REG_DWORD:
                value = int(value)
            win32api.RegSetValueEx(hreg, valueName, 0, type, value)
        except Exception,e:
            return False
        finally:
            if hreg:
                win32api.RegCloseKey(hreg)
        return True
            

def delKeyValue(keyFullName, valueName,reDirect = False,byDriver = False):
    if byDriver:
        if hasKey(keyFullName, byDriver): 
            return __getQADriver__().DelKeyValueEx(keyFullName,valueName,reDirect)
    else:
        if hasKey(keyFullName,reDirect):
            hreg = None
            rootKeyName, subKeyName = _getRootAndSub(keyFullName)
            try:
                hreg = win32api.RegOpenKeyEx(rootKeyName, subKeyName, 0, getSamDesired(win32con.KEY_WRITE,reDirect))
                win32api.RegDeleteValue(hreg, valueName)
            except:
                return False
            finally:
                if hreg:
                    win32api.RegCloseKey(hreg)
    return True

def backupKey(keyFullName, backupFileName):
    cmd = r'REG SAVE %s "%s" /y 1> NUL 2> NUL' % (keyFullName, backupFileName)
    if os.system(cmd) != 0:
        raise Exception('备份注册表键失败！%s' % keyFullName)

def restoreKey(keyFullName, backupFileName):
    addKey(keyFullName)
    cmd = r'REG RESTORE %s "%s" 1> NUL 2> NUL' % (keyFullName, backupFileName)
    if os.system(cmd) != 0:
        raise Exception('恢复注册表键失败！%s' % keyFullName)


def transKeyName(keyName):
    keyName = keyName.upper()
    if keyName in ['HKLM', 'HKEY_LOCAL_MACHINE']:
        keyName = win32con.HKEY_LOCAL_MACHINE
    elif keyName in ['HKCR', 'HKEY_CLASSES_ROOT']:
        keyName = win32con.HKEY_CLASSES_ROOT
    elif keyName in ['HKCU', 'HKEY_CURRENT_USER']:
        keyName = win32con.HKEY_CURRENT_USER
    elif keyName in ['HKU', 'HKEY_USERS']:
        keyName = win32con.HKEY_USERS
    elif keyName in ['HKCC', 'HKEY_CURRENT_CONFIG']:
        keyName = win32con.HKEY_CURRENT_CONFIG
    return keyName

def _getRootAndSub(keyFullName):
    nameList = keyFullName.split('\\', 1)
    rootKeyName = transKeyName(nameList[0])
    subKeyName = None
    if len(nameList) == 2:
        subKeyName = nameList[1]
    return rootKeyName, subKeyName

def _openKey(keyName, subKeyName = None):
    try:
        return win32api.RegOpenKeyEx(keyName, subKeyName, 0, win32con.KEY_ALL_ACCESS)
    except:
        return None

def _getAllValue(key):
    res = {}
    index = 0
    while True:
        try:
            name, value, type = win32api.RegEnumValue(key, index)
            res[name] = (value, type)
            index += 1
        except:
            break
    return res

#得到注册表键及其所有子键的值信息
#参数:
#   keyFullName:键全名
#此操作返回一个dict，以注册表键全名为dict的键，以注册表键的值为了dict的值
#当键不存在时返回空dict
def getRegTreeInfo(keyFullName):
    stack = [keyFullName]
    res = {}
    while len(stack) != 0:
        keyFullName = stack.pop()
        rootKeyName, subKeyName = _getRootAndSub(keyFullName)
        key = _openKey(rootKeyName, subKeyName)
        if not key:
            break
        #枚举value
        valueMap = _getAllValue(key)
        res[keyFullName] = valueMap
        #枚举子项
        keyNameList = list(win32api.RegEnumKeyEx(key))
        for keyName in keyNameList:
            stack.append(os.path.join(keyFullName, keyName[0]))
        win32api.RegCloseKey(key)
    return res

def importRegFile(regFile):    
    cmd = r'REG IMPORT "%s" 1> NUL 2> NUL '%(regFile)
    os.system(cmd)
    if os.system(cmd) != 0:
        raise Exception('导入注册文件失败:"%s"' % regFile)
    
def __listFile__(path, isDeep=True):
    import glob
    _list = []
    if isDeep:
        try:
            for root, dirs, files in os.walk(path):
                for fl in files:
                    _list.append('%s\%s' % (root, fl))                
        except:
            pass
    else:
        for fn in glob.glob( path + os.sep + '*' ):
            if not os.path.isdir(fn):
                _list.append('%s' % path + os.sep + fn[fn.rfind('\\')+1:])
    return _list

def __listFile(remotePath, exclude=None, isDeep=True):
    _list = []
    _subdir = []
    _delList = []
    # 本地
    _list = __listFile__(remotePath, isDeep)
    if not _list:return _list
    
    if exclude and type(exclude)==list:
        for extFile in exclude:
            for fp in _list:
                if extFile.lower() == os.path.basename(fp).lower():
                    _delList.append(fp)
    if _delList:
        for delfp in _delList:
            _list.remove(delfp)
    return _list

def importRegFileByFolder(folderName,fileList=None):
##    import CommonFun
##    folderName = CommonFun.getNormalPath(folderName)
    files = []
    if fileList and type(fileList) == list:
        for filename in fileList:
            filepath = os.path.join(folderName,filename)
            files.append(filepath)
    else:
        files = __listFile(folderName)
    for file in files:
        importRegFile(file)
        
def LoadReg(foldPath, exclude=None, isDeep=True):
    _reg = []
    _reg = autofile.listFile(foldPath, exclude, isDeep)
    if not _reg:
        return False
    for reg in _reg:
        importRegFile(reg)
    return True   
            
if __name__ == '__main__':    
#    print addKey(r'HKEY_LOCAL_MACHINE\SOFTWARE\360Safe\360Scassn\test')
    print hasKey(r'HKEY_CURRENT_USER\Software\360SoftMgr',True,True)    
#    print setKeyValue(r'HKEY_LOCAL_MACHINE\SOFTWARE\test\a\b','test',win32con.REG_DWORD,'4')
#    print delKeyValue(r'HKEY_LOCAL_MACHINE\SOFTWARE\360Safe\360Scassn\test','test')
#    print delKey(r'HKEY_LOCAL_MACHINE\SOFTWARE\360Safe\360Scassn\test')
#    print getKeyValue(r'HKEY_LOCAL_MACHINE\SOFTWARE\360Safe\360Scassn\test','test')
#    print hasKeyValue(r'HKEY_LOCAL_MACHINE\SOFTWARE\360Safe\360Scassn\test','test')
#    print getRegTreeInfo(r'HKEY_LOCAL_MACHINE\SOFTWARE\Intel')
#    print Enum(r'HKEY_LOCAL_MACHINE\SOFTWARE\test')
#    print delKey(r'HKEY_LOCAL_MACHINE\SOFTWARE\test')
    pass