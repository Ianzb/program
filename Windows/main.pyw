from window import *

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    translator = FluentTranslator()
    app.installTranslator(translator)
    w = Window()
    w.show()
    if program.isStartup and setting.read("autoHide"):
        w.hide()
    app.exec_()
