#coding:GBK
#------文件操作------
import os,sys,re,win32con, win32api,configobj,zipfile,pythoncom,uuid
from win32com.shell import shell
import xml.etree.ElementTree as ET

import autocfg
###############     基础函数             ##############################
extEnviron = os.environ
def __need_break__(envList, backup):
    if not envList:
        return True
    ret = True
    for name in envList:
        if name in backup:
            return True
    for name in envList:
        if name.strip('%').upper() in extEnviron:
            ret = False
    return ret

#得到正常路径
#参数:
#   path: 路径，其中可以包含系统环境变量，如%appdata%等
def getNormalPath(path):
    tmpPath = os.path.expandvars(path)
    if os.path.exists(tmpPath):
        tmpPath = win32api.GetLongPathName(tmpPath)
    return tmpPath

def existPath(path):
    path = getNormalPath(path)
    return os.path.exists(path)

def combinePath(path1, path2):
    return os.path.join(path1, path2)

def changeExtName(path, newExtName):
    newExtName = newExtName.strip()
    if not newExtName.startswith('.'):
        newExtName = '.' + newExtName
    return os.path.splitext(path)[0] + newExtName

###############     文件读写操作相关     ##############################
#文件属性
def getFileAttribStr(filePath):
    iFileAttr = win32api.GetFileAttributes(filePath)
    _str = ''
    attr_map = {'FILE_ATTRIBUTE_READONLY':0x01,
                'FILE_ATTRIBUTE_HIDDEN':0x02,
                'FILE_ATTRIBUTE_COMPRESSED':0x800,
                'LE_ATTRIBUTE_DIRECTORY':0x10,
                'FILE_ATTRIBUTE_ENCRYPTED':0x4000,
                'FILE_ATTRIBUTE_NORMAL':0x80,
                'FILE_ATTRIBUTE_ARCHIVE':0x20,
                'FILE_ATTRIBUTE_SYSTEM':0x4,
                'FILE_ATTRIBUTE_TEMPORARY':0x100,
                'FILE_ATTRIBUTE_DEVICE':0x40,
                'FILE_ATTRIBUTE_NOT_CONTENT_INDEXED':0x2000,
                'FILE_ATTRIBUTE_OFFLINE':0x1000,
                'FILE_ATTRIBUTE_REPARSE_POINT':0x400,
                'FILE_ATTRIBUTE_SPARSE_FILE':0x200,
                'FILE_ATTRIBUTE_VIRTUAL':0x10000}
    for key in attr_map.keys():
        if iFileAttr & attr_map[key]:
            if _str:
                _str += '|%s'%(key)
            else:
                _str += '%s'%(key)
    return _str

def setFileAttribute(filePath, attrib, inherit = True):
    _filePath = []
    if type(filePath) == str:
        filePath = getNormalPath(filePath)        
        if os.path.exists(filePath):
            _filePath.append(filePath)
    elif type(filePath) == list:
        for file in filePath:
            if os.path.exists(file):
                _filePath.append(file)
    if not _filePath:
        return None
    for _file in _filePath:
        if os.path.isfile(_file):
            cmd = 'attrib %s "%s" 1>NUL 2>NUL'%(attrib, _file)
            os.system(cmd)
        elif os.path.isdir(_file):
            if inherit:
                cmd = 'attrib %s "%s" 1>NUL 2>NUL'%(attrib, _file)
                os.system(cmd)
                cmd = 'attrib %s "%s\*.*" /S /D 1>NUL 2>NUL'%(attrib, _file)
            else:
                cmd = 'attrib %s "%s" 1>NUL 2>NUL'%(attrib, _file)
            os.system(cmd)
    return True

def isFileHidden(path):
    path = getNormalPath(path)
    return win32api.GetFileAttributes(path) & 2 == 2

def hideFile(path, hidden = True):
    if hidden:
        setFileAttribute(path, '+h')
    else:
        setFileAttribute(path, '-h')
#文件操作
def createFolder(path):
    path = getNormalPath(path)
    try:
        if os.path.exists(path):
            return False
        os.makedirs(path)        
        return path
    except:
        return False
    return True

def createFile(path, content = '', mode = 'w', attr = None):
    try:
        path = getNormalPath(path)
        index = path.rfind('\\')
        if index > 0:
            if not existPath(path[0:index]):
                createFolder(path[0:index])
        f = open(path, mode)
        if content:
            f.write(content)
        f.close()
        if attr:
            setFileAttribute(path, attr)        
        return path
    except Exception,e:
        return False
    return True

def setFileData(filename, openType, data):
    file = open(filename, openType)
    file.write(data)
    file.close()

def copyFile(sourceFile, destFile):
    sourceFile = getNormalPath(sourceFile)
    destFile = getNormalPath(destFile)
    if not os.path.exists(sourceFile):
        return False
    if os.path.exists(destFile):
        os.system('del /F "%s"'%(destFile,))
    destPath = os.path.dirname(destFile)
    if not os.path.exists(destPath):
        createFolder(destPath)
    if win32api.CopyFile(sourceFile,destFile,False) == 0:
        return False
    return True
        
def renameFile(sourceFile, destFile):
    sourceFile = getNormalPath(sourceFile)
    destFile = getNormalPath(destFile)
    if not os.path.exists(sourceFile):
        return False
    sourceFolder = os.path.dirname(sourceFile)
    destFile = os.path.join(sourceFolder, os.path.basename(destFile))
    if os.path.exists(destFile):
        try:
            os.remove(destFile)
        except:
            return False
    try:
        os.rename(sourceFile, destFile)
    except:
        return False
    return True

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

def listFile(remotePath, exclude=None, isDeep=True):
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

def deleteFile(path):
    import glob
    path = getNormalPath(path)
    for filePath in glob.glob(path):
        if not os.path.isfile(filePath):
            continue
        try:
            os.remove(filePath)
        except Exception,e:
            continue
    return True

def copyFolder(sourceFolder,destFolder,fileList=None):    
    sourceFolder = getNormalPath(sourceFolder)
    destFolder = getNormalPath(destFolder)    
    if fileList:
        for filepath in fileList:
            copyFile(combinePath(sourceFolder,filepath),combinePath(destFolder,filepath))
    else:
        cmd = 'xcopy "%s" "%s" /R /E /I /H /Y 1>NUL 2>NUL' % (sourceFolder, destFolder)
        if os.system(cmd) != 0:
            return False                      
    return True

def deleteFolder(path):
    import shutil
    import glob
    path = getNormalPath(path)
    for folderPath in glob.glob(path):
        if not os.path.isdir(folderPath):
            continue
        setFileAttribute(folderPath, '-R')
        os.system('rd /s /q "%s" 1> NUL 2> NUL' % folderPath)

def __copyTo__(source, dest, destSubPath, destName):
    destName = getNormalPath(destName)
    destPath = os.path.join(dest, destSubPath)
    destPath = os.path.join(destPath, destName)
    copyFile(source, destPath)
    return os.path.join(destSubPath, destName)

def copyToDesktop(source, destSubPath, destName):
    dest = __copyTo__(source, autocfg.GetDesktopPath(), destSubPath, destName)
    return os.path.join(autocfg.GetDesktopPath(), dest)

def copyToStartMenu(source, destSubPath, destName):
    dest = __copyTo__(source, autocfg.GetStartMenuPath(), destSubPath, destName)
    return os.path.join(autocfg.GetStartMenuPath(), dest)

def copyToFavorites(source, destSubPath, destName):
    dest = __copyTo__(source, autocfg.GetFavoritePath(), destSubPath, destName)
    return os.path.join(autocfg.GetFavoritePath(), dest)

def copyToQuickLaunch(source, destSubPath, destName):
    dest = __copyTo__(source, autocfg.GetQuickLaunchPath(), destSubPath, destName)
    return os.path.join(autocfg.GetQuickLaunchPath(), dest)

def copyToPrograms(source, destSubPath, destName):
    dest = __copyTo__(source, autocfg.GetProGramsPath(), destSubPath, destName)
    return os.path.join(autocfg.GetProGramsPath(), dest)

def createDesktopFile(fileName, content = ''):
    return createFile(os.path.join(autocfg.GetDesktopPath(), fileName), content)

def createDesktopFolder(folderName):
    return createFolder(os.path.join(autocfg.GetDesktopPath(), folderName))

def createStartMenuFile(fileName, content = ''):
    return createFile(os.path.join(autocfg.GetStartMenuPath(), fileName), content)

def createStartMenuFolder(folderName):
    return createFolder(os.path.join(autocfg.GetStartMenuPath(), folderName))

def createFavoritesFile(fileName, content = ''):
    return createFile(os.path.join(autocfg.GetFavoritePath(), fileName), content = '')

def createFavoritesFolder(folderName):
    return createFolder(os.path.join(autocfg.GetFavoritePath(), folderName))

def createProgramsFile(fileName, content = ''):
    return createFile(os.path.join(autocfg.GetProGramsPath(), fileName), content)

def createProgramsFolder(folderName):
    return createFolder(os.path.join(autocfg.GetProGramsPath(), folderName))

def createQuickLaunchFile(fileName, content = ''):
    return createFile(os.path.join(autocfg.GetQuickLaunchPath(), fileName), content)

def createQuickLaunchFolder(folderName):
    return createFolder(os.path.join(autocfg.GetQuickLaunchPath(), folderName))

###############      ini操作类       ##############################
def getIniDict(ini_path):
    ini_path = getNormalPath(ini_path)
    ini_map = {}
    if not os.path.exists(ini_path):
        return ini_map
    config=configobj.ConfigObj(ini_path,list_values=False)
    keys = config.keys()
    for key in keys:
        ini_map[key] = {}
        dict = config[key]
        if type(dict) == str:
            continue
        for (k,v) in dict.items():
            ini_map[key][k] = v
    return ini_map

def writeDicToFile(dict, ini_path):
    ini_path = getNormalPath(ini_path)  
    content = ''
    for (k,v) in dict.items():
        content = content + '[' + k + ']\r\n'
        for (k1,v1) in v.items():
            content += k1 + '=' + v1 + '\r\n'
    try:
        f = file(ini_path,'w')
        f.write(content)
        f.close()
    except Exception,e:
        return False
    return True
        
def getIniValue(ini_path,sectionName,optionName):
    ini_path = getNormalPath(ini_path)    
    if not os.path.exists(ini_path):
        return None
    try:
        config = configobj.ConfigObj(ini_path)
        value = config[sectionName][optionName]
        return value
    except Exception,e:
        return None

def modifyIniValue(ini_path,sectionName,optionName,value):
    ini_path = getNormalPath(ini_path)    
    if not os.path.exists(ini_path):
        return False
    if os.path.exists(ini_path):        
        dict = getIniDict(ini_path)
    else:
        dict = {}
        dict[sectionName] = {}
    try:
        if not dict.has_key(sectionName):
            dict[sectionName] = {}
        dict[sectionName][optionName] = value
        writeDicToFile(dict,ini_path)
    except Exception,e:        
        return False
    return True

def removeIniOption(ini_path,sectionName,optionName):
    ini_path = getNormalPath(ini_path)
    if not os.path.exists(ini_path):
        return False
    config=configobj.ConfigObj(ini_path)
    try:
        dict = config[sectionName]
        dict.pop(optionName)
        config.write()
    except Exception,e:
        return False
    return True

def addIniOption(ini_path,sectionName,optionName,optionValue):
    ini_path = getNormalPath(ini_path)
    if not os.path.exists(ini_path):
        return False
    config=configobj.ConfigObj(ini_path)
    try:
        config[sectionName][optionName] = optionValue
        config.write()
    except Exception,e:
        return False
    return True

def removeIniOptionByValue(ini_path,value):
    ini_path = getNormalPath(ini_path)    
    if not os.path.exists(ini_path):
        return False
    dict = getIniDict(ini_path)
    for (k,v) in dict.items():
        for (k1,v1) in v.items():
            if v1 == value:
                v.pop(k1)
                if v == None or v.__len__() == 0:
                    dict.pop(k)
                writeDicToFile(dict,ini_path)
                return True

def verifyOptionExist(ini_path, option, section=None):
    ini_path = getNormalPath(ini_path)    
    if not os.path.exists(ini_path):
        return False
    config=configobj.ConfigObj(ini_path)
    try:
        for key in config.keys():
            if section and key != section:
                continue
            dict = config[key]
            for (k,v) in dict.items():
                if k == option:
                    return True
    except Exception,e:
        return False
    return False

def verifyValueExist(ini_path,value):
    ini_path = getNormalPath(ini_path)
    if not os.path.exists(ini_path):
        return False
    config=configobj.ConfigObj(ini_path)
    try:
        for key in config.keys():
            dict = config[key]
            for (k,v) in dict.items():
                if v == value:
                    return True
    except Exception,e:
        return False
    return False

def __LoadIniDict__(ini_path):
    ini_path = getNormalPath(ini_path)    
    content = []
    _dic = {}
    if not os.path.exists(ini_path):
        print 'Invalid path: %s' % ini_path
        sys.exit(1)
    try:
        f = open(ini_path, 'rb')
    except:
        return None
    content = f.readlines()
    f.close()
    
    for line in content:
        if line.strip().startswith('#'):#过滤掉ini中的注释
            continue
        res = re.match(r'^\[(.*?)\]', line.strip())
        if res:
            (session, ) = res.groups()
            session = session.lower()
            current = session
            if _dic.has_key(session):pass
            else:_dic[session] = []
        else:
            res = re.match(r'^(.*?)=(.*)$', line.strip())
            if res:
                (opt, value) = res.groups()
                if opt.lower() not in _dic[current]:
                    _dic[current].append((opt.lower(), value.lower()))
                else:pass
            else:
                if line.strip():
                    return None
    return _dic

def compareIni(iniSrc, iniDest):
    srcContent = __LoadIniDict__(iniSrc)
    destContent = __LoadIniDict__(iniDest)
    if (not srcContent) or (not destContent):
        return False
    #第一层的对比
    src_keys = srcContent.keys()
    dest_keys = destContent.keys()
    src_keys_set = set(src_keys)
    dest_keys_set = set(dest_keys)
    if src_keys_set ^ dest_keys_set:
        return False
    #第二层对比
    keys = src_keys = dest_keys
    for key in keys:
        src_option_value = srcContent[key]
        dest_option_value = destContent[key]
        src_option_value_set = set(src_option_value)
        dest_option_value_set = set(dest_option_value)
        if src_option_value_set ^ dest_option_value_set:
            return False
    return True
###############         xml函数       ################################
def modifyXMLValue(xml_Path, node_path, value):
    node_list = []
    xml_Path = getNormalPath(xml_Path)
    if os.path.exists(xml_Path):
        os.remove(xml_Path)
    node_list = node_path.split('\\')
    if not node_list:
        return False
    root = ET.Element(node_list[0])
    tree = ET.ElementTree(root)
    parent = None
    for i in range(1,len(node_list)):
        if i == 1:
            parent = root
        sub = ET.SubElement(parent, node_list[i])
        parent = sub
        if i == (len(node_list) - 1):
            sub.text = value
    if not os.path.exists(os.path.dirname(xml_Path)):
        createFolder(os.path.dirname(xml_Path))
    tree.write(xml_Path, 'utf-8')
    
###############      快捷方式函数       ##############################
#创建正常格式的快捷方式
def createLnk(target, path, name, iconPath = None, iIcon = 0, arguments = None):
    shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink,
                                          None,
                                          pythoncom.CLSCTX_INPROC_SERVER,
                                          shell.IID_IShellLink)
    if target:
        shortcut.SetPath(target)
    if iconPath:
        iconPath = getNormalPath(iconPath)
        shortcut.SetIconLocation(iconPath, iIcon)
    if arguments:
        shortcut.SetArguments(arguments)

    if os.path.splitext(name)[-1] != '.lnk':
        name += '.lnk'
    path = getNormalPath(path)
    name = getNormalPath(name)
    path = os.path.join(path, name)
    try:
        if not os.path.exists(os.path.dirname(path)):
            createFolder(os.path.dirname(path))
        shortcut.QueryInterface(pythoncom.IID_IPersistFile).Save(path, 0)        
        return path
    except Exception, e:
        return False
    return True

def createDesktopLnk(target, name, iconPath = None, iIcon = 0, arguments = None):
    return createLnk(target, '%desktop%', name, iconPath, iIcon, arguments)

def createRootLnk(target, rootPath, subPath, name, iconPath = None, iIcon = 0, arguments = None):
    return createLnk(target, os.path.join(rootPath, subPath), name, iconPath, iIcon, arguments)

def createStartMenuLnk(target, subPath, name, iconPath = None, iIcon = 0, arguments = None):
    return createRootLnk(target, '%startmenu%', subPath, name, iconPath, iIcon, arguments)

def createFavoritesLnk(target, subPath, name, iconPath = None, iIcon = 0, arguments = None):
    return createRootLnk(target, '%favorites%', subPath, name, iconPath, iIcon, arguments)

def createProgramsLnk(target, subPath, name, iconPath = None, iIcon = 0, arguments = None):
    return createRootLnk(target, '%programs%', subPath, name, iconPath, iIcon, arguments)

def createQuickLanuchLnk(target, subPath, name, iconPath = None, iIcon = 0, arguments = None):
    return createRootLnk(target, '%quicklaunch%', subPath, name, iconPath, iIcon, arguments)

#从正常格式的快捷方式中得到目标指向
def getTargetFromLink(lnkPath):
    lnkPath = getNormalPath(lnkPath)
    shortcut = pythoncom.CoCreateInstance(shell.CLSID_ShellLink,
                                          None,
                                          pythoncom.CLSCTX_INPROC_SERVER,
                                          shell.IID_IShellLink)
    shortcut.QueryInterface(pythoncom.IID_IPersistFile).Load(lnkPath)
    path = None
    try:
        path = shortcut.GetPath(shell.SLGP_UNCPRIORITY)
    except Exception,e:
        return None
    return path[0].lower()

###############      url函数       ###################################
#创建正常格式的url快捷方式
def createUrl(url, path, name):
    shortcut = pythoncom.CoCreateInstance(shell.CLSID_InternetShortcut,
                                          None,
                                          pythoncom.CLSCTX_INPROC_SERVER,
                                          shell.IID_IUniformResourceLocator)
    shortcut.SetURL(url)
    if os.path.splitext(name)[-1] != '.url':
        name += '.url'

    path = getNormalPath(path)
    name = getNormalPath(name)
    path = os.path.join(path, name)
    try:
        if not os.path.exists(os.path.dirname(path)):
            createFolder(os.path.dirname(path))
        shortcut.QueryInterface(pythoncom.IID_IPersistFile).Save(path, 0)        
        return path
    except:
        return False
    return True

def createDesktopUrl(url, name):
    return createUrl(url, '%desktop%', name)

def createRootUrl(url, rootPath, subPath, name):
    return createUrl(url, os.path.join(rootPath, subPath), name)

def createStartMenuUrl(url, subPath, name):
    return createRootUrl(url, '%startmenu%', subPath, name)

def createFavoritesUrl(url, subPath, name):
    return createRootUrl(url, '%favorites%', subPath, name)

def createProgramsUrl(url, subPath, name):
    return createRootUrl(url, '%programs%', subPath, name)

def createQuickLanuchUrl(target, subPath, name):
    return createRootUrl(target, '%quicklaunch%', subPath, name)

#从.url快捷方式获取url连接地址
def getURLFromShortcut(urlPath):
    urlPath = getNormalPath(urlPath)
    shortcut = pythoncom.CoCreateInstance(shell.CLSID_InternetShortcut, None, pythoncom.CLSCTX_INPROC_SERVER,shell.IID_IUniformResourceLocator)
    shortcut.QueryInterface(pythoncom.IID_IPersistFile).Load(urlPath)
    url = None
    try:
        url = shortcut.GetURL()
    except Exception,e:
        return None
    return url

###############      zipfile函数       ##############################
def compressFiles(filePath, zipFileName):
    Flag = True
    _list = []
    if os.path.isdir(filePath):
        _list = listFile(filePath)
    elif os.path.isfile(filePath):
        _list.append(filePath)
        Flag = False
    else:return False
    if os.path.exists(zipFileName):
        try:os.remove(zipFileName)
        except:return False
    try:
        f = zipfile.ZipFile(zipFileName, 'w', zipfile.ZIP_DEFLATED)
    except:
        return False
    for file in _list:
        try:
            if Flag:
                f.write(os.path.abspath(file), os.path.relpath(os.path.abspath(file), filePath))
            else:
                f.write(os.path.abspath(file), os.path.basename(filePath))
        except:
            if f:
                f.close()
            return False
    if f:
        f.close()
    return True

def unCompressFiles(zipFileName, destFolder = os.getcwd()):
    if not os.path.exists(zipFileName):return False
    try:
        z = zipfile.ZipFile(zipFileName, 'r')
    except:
        return False
    for i in range(len(z.namelist())):
        try:
            createFile(os.path.join(destFolder, os.path.relpath(os.path.abspath(z.namelist()[i]), os.getcwd())), z.read(z.namelist()[i]), 'wb')
        except:
            if z:
                z.close()
            return False
    if z:
        z.close()
    return True

