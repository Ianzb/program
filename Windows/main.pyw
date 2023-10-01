# 加载code文件夹
import os, sys

if ":\WINDOWS\system32".lower() in os.getcwd().lower():
    auto_start = True
    os.chdir(os.path.dirname(sys.argv[0]))
    sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "code"))
else:
    auto_start=False
    sys.path.append("code")
# 窗口初始化
from main_window import *

saveSetting("pid", abs_pid)

QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

QApplication.processEvents()
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
translator = FluentTranslator(QLocale())
app.installTranslator(translator)
w = MainWindow()
# 展示窗口
if not auto_start:
    w.showMaximized()
else:
    w.hide()
    if readSetting("autoupdate") == "1":
        w.settingInterface.aboutCard.btn2()
app.exec_()
