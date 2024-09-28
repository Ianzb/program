import sys


@property
def WINDOWS_VERSION():
    """
    获得Windows版本
    @return: 返回列表，例：[10,0,22631]
    """
    version = sys.getwindowsversion()
    return [version.major, version.minor, version.build]


@property
def DESKTOP_PATH():
    """
    获得桌面路径
    @return: 桌面路径
    """
    from winreg import QueryValueEx,OpenKey, HKEY_CURRENT_USER
    return QueryValueEx(OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "Desktop")[0]


@property
def DOWNLOAD_PATH():
    """
    获得下载路径
    @return: 桌面路径
    """
    from winreg import QueryValueEx,OpenKey, HKEY_CURRENT_USER
    return QueryValueEx(OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"), "{374DE290-123F-4565-9164-39C4925E467B}")[0]
