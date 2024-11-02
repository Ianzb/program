from source import *

window = Window()
if program.isStartup and setting.read("autoHide"):
    window.hide()
    log.info("程序主窗口隐藏！")
else:
    window.show()
    log.info("程序主窗口展示！")
app.exec()

from source.addon import *
