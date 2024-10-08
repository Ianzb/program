import os, sys
from winreg import QueryValueEx, OpenKey, HKEY_CURRENT_USER

USER_PATH = os.path.expanduser("~")  # 系统用户路径
REQUEST_HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"}  # 程序默认网络请求头
WINDOWS_VERSION = [sys.getwindowsversion().major, sys.getwindowsversion().minor, sys.getwindowsversion().build]
DESKTOP_PATH = QueryValueEx(OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "Desktop")[0]
DOWNLOAD_PATH = QueryValueEx(OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "{374DE290-123F-4565-9164-39C4925E467B}")[0]
