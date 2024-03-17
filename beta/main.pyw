from source.window import *

QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

app = QApplication(sys.argv)
translator = FluentTranslator()
app.installTranslator(translator)
window = Window()
if program.isStartup and setting.read("autoHide"):
    window.hide()
    logging.debug("主窗口隐藏")
else:
    window.show()
    logging.debug("主窗口展示")
app.exec()
logging.info("程序运行成功")
