import sys
from cx_Freeze import setup, Executable

base = None
if(sys.platform == "win32"):
    base = "Win32GUI"

setup(name = "WinFling",
      version = "0.1",
      description = "Easily Launch Windows Programs",
      options = {'build_exe': {'include_files':["thumbnail.png", "config.example.ini"]}},
      executables = [Executable("winfling.py", base=base)])