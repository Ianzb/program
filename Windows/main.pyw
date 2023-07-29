from zb import *
from main_window import *

saveSetting("pid", abs_pid)

QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
translator = FluentTranslator(QLocale())
app.installTranslator(translator)
w = MainWindow()
w.show()
if ":\WINDOWS\system32".lower() in old_path.lower():
    w.hide()
    if readSetting("autoupdate") == "1":
        w.settingInterface.aboutCard.btn2()
app.exec_()
