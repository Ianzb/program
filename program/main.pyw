from source import *

window = Window()
if program.isStartup and setting.read("autoHide"):
    window.hide()
    window.setWindowOpacity(1)
    logging.info("程序主窗口隐藏！")
else:
    window.show()
    logging.info("程序主窗口展示！")
app.exec()

import source.addon
