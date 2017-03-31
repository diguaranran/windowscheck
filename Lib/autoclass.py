#coding:GBK
import ctypes

class RECT(ctypes.Structure):
    _fields_=[('left', ctypes.c_long),
              ('top', ctypes.c_long),
              ('right', ctypes.c_long),
              ('bottom', ctypes.c_long)]

class Version():
    def __init__(self,versionString):
        versionList = []
        try:
            versionList = versionString.split('.')
        except:
            raise 'invalid version string'
        self.MajorPart = int(versionList[0])
        self.MinorPart = int(versionList[1])
        self.BuildPart = int(versionList[2])
        if len(versionList) == 4:
            self.PrivateBuild = int(versionList[3])
        else:
            self.PrivateBuild = None

    def __gt__(self,other):
        if self.MajorPart > other.MajorPart:
            return True
        if self.MinorPart > other.MinorPart:
            return True
        if self.BuildPart > other.BuildPart:
            return True
        if not self.PrivateBuild:
            if self.PrivateBuild > other.PrivateBuild:
                return True
        return False

    def __lt__(self,other):
        if self.MajorPart < other.MajorPart:
            return True
        if self.MinorPart < other.MinorPart:
            return True
        if self.BuildPart < other.BuildPart:
            return True
        if not self.PrivateBuild:
            if self.PrivateBuild < other.PrivateBuild:
                return True
        return False

    def __eq__(self,other):
        if self.MajorPart == other.MajorPart:
            return True
        if self.MinorPart == other.MinorPart:
            return True
        if self.BuildPart == other.BuildPart:
            return True
        if not self.PrivateBuild:
            if self.PrivateBuild == other.PrivateBuild:
                return True
        return False

class TBBUTTON(ctypes.Structure):
    _fields_ = [
        ('iBitmap', ctypes.c_uint),
        ('idCommand', ctypes.c_uint),
        ('fsState', ctypes.c_byte),
        ('fsStyle', ctypes.c_byte),
        ('bReserved1', ctypes.c_byte),
        ('bReserved2', ctypes.c_byte),
        ('dwData', ctypes.c_uint),
        ('iString', ctypes.c_uint)
    ]

class TVITEM(ctypes.Structure):
    _fields_ = [
        ('mask', ctypes.c_uint),
        ('hItem', ctypes.c_uint),
        ('state', ctypes.c_uint),
        ('stateMask', ctypes.c_uint),        
        ('pszText', ctypes.c_uint),
        ('cchTextMax', ctypes.c_int),
        ('iImage', ctypes.c_int),
        ('iSelectedImage', ctypes.c_int),
        ('cChildren', ctypes.c_int),
        ('lParam', ctypes.c_uint)
    ]

class LVITEM(ctypes.Structure):
    _fields_ = [
        ('mask', ctypes.c_uint),
        ('iItem', ctypes.c_int),
        ('iSubItem', ctypes.c_int),
        ('state', ctypes.c_uint),
        ('stateMask', ctypes.c_uint),
        ('pszText', ctypes.c_char_p),
        ('cchTextMax', ctypes.c_int),
        ('iImage', ctypes.c_int),
        ('lParam', ctypes.c_uint)
    ]

class MENUITEMINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', ctypes.c_uint),
        ('fMask', ctypes.c_int),
        ('fType', ctypes.c_int),
        ('fState', ctypes.c_uint),
        ('wID', ctypes.c_uint),
        ('hSubMenu', ctypes.c_void_p),
        ('hbmpChecked', ctypes.c_void_p),
        ('hbmpUnchecked', ctypes.c_void_p),
        ('dwItemData', ctypes.c_long),
        ('dwTypeData', ctypes.c_char_p),
        ('cch', ctypes.c_uint),
        ('hbmpItem', ctypes.c_uint),
    ]    