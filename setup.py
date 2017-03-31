#-*- coding: cp936 -*-
# ...
# ModuleFinder can't handle runtime changes to __path__, but win32com uses them
try:
    # py2exe 0.6.4 introduced a replacement modulefinder.
    # This means we have to add package paths there, not to the built-in
    # one.  If this new modulefinder gets integrated into Python, then
    # we might be able to revert this some day.
    # if this doesn't work, try import modulefinder
    try:
        import py2exe.mf as modulefinder
    except ImportError:
        import modulefinder
    import win32com, sys
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]: #,"win32com.mapi"
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass

from distutils.core import setup
import py2exe

# ...
# The rest of the setup file.
# ...
import glob
import py2exe

includes = ["encodings", "encodings.*", "sip"]
options = {"py2exe":
               {"compressed": 1,
                "optimize": 2,
                "ascii": 1,
                "includes":includes,
                "bundle_files": 1,
                "dll_excludes":['w9xpopen.exe', 'mswsock.dll', 'MSWSOCK.dll', 'powrprof.dll','MSVCP90.dll']},
           }
setup(windows=[{"script": "runProject.py"}],
        options = options,
#        data_files = [('config', [r'config\userInfo.ini']),
#                      ('static', [glob.glob(r'static\*.html')]),
#                      ('requests', []),
#                      ('jsFile', []),
#                      ('Lib', []),
#                      ('temp', [glob.glob(r'temp\*.*')])],
        zipfile=None,)