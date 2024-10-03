from source import *

window = Window()
window.show()
if program.isStartup and setting.read("autoHide"):
    window.hide()
    logging.info("程序主窗口隐藏！")
else:
    logging.info("程序主窗口展示！")
app.exec()
