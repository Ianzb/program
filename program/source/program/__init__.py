from .program import *
from .setting import *

QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
app = QApplication(sys.argv)
translator = FluentTranslator()
app.installTranslator(translator)
# 关闭SSL证书验证
import ssl

ssl._create_default_https_context = ssl._create_unverified_context()

# 日志设置
open(program.LOGGING_FILE_PATH, "w").close() if not f.existPath(program.LOGGING_FILE_PATH) or f.fileSize(program.LOGGING_FILE_PATH) >= 1024 * 128 else None

handler2 = logging.FileHandler(program.LOGGING_FILE_PATH, encoding="utf-8")
handler2.setLevel(logging.DEBUG)
handler2.setFormatter(logging.Formatter("[%(levelname)s %(asctime)s %(filename)s %(process)s]:%(message)s"))

log.addHandler(handler2)

log.info(f"程序启动参数{program.STARTUP_ARGUMENT}!")

program.detectRepeatRun()

log.info("程序动态数据api初始化成功！")
