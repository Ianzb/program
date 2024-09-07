from source import *

QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
app = QApplication(sys.argv)
translator = FluentTranslator()
app.installTranslator(translator)
window = Window()
window.show()
if program.isStartup and setting.read("autoHide"):
    window.hide()
    logging.info("主窗口隐藏")
else:
    logging.info("主窗口展示")
app.exec()
logging.info("程序运行成功")
