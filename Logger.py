#coding:gbk
import os
import ctypes
import time

FOREGROUND_BLUE = 0x01 # text color contains blue.
FOREGROUND_GREEN= 0x02 # text color contains green.
FOREGROUND_RED  = 0x04 # text color contains red.

FOREGROUND_INTENSITY = 0x08 # text color is intensified.


class printLog():
    '''打印log信息'''
    def __init__(self):
        self._std_out_handle = ctypes.windll.kernel32.GetStdHandle(-11)

    def __set_cmd_text_color(self,color):
        '''(color) -> BOOL Example: set_cmd_text_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)'''
        bool = ctypes.windll.kernel32.SetConsoleTextAttribute(self._std_out_handle, color)
        return bool

    def __resetColor(self):
        '''重新设置成黑白色'''
        self.__set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)

    def Error(self, error):
        nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        msg = '[' + nowTime + '] Error: ' + error + os.linesep
        self.__set_cmd_text_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
        print('%s'%msg)
        self.__resetColor()

    def Pass(self, text):
        nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        msg = '[' + nowTime + '] Pass: ' + text + os.linesep
        self.__set_cmd_text_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        print('%s'%msg)
        self.__resetColor()

    def Comment(self, comment):
        nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        msg = '[' + nowTime + '] Comment: ' + comment + os.linesep
        print('%s'%msg)

def LogError(msg):
    printLog().Error(msg)

def LogComment(msg):
    printLog().Comment(msg)

def LogPass(msg):
    printLog().Pass(msg)