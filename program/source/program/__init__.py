from logging.config import dictConfig

from .program import *
from .setting import *
import logging

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
open(program.LOGGING_FILE_PATH, "w").close() if not zb.existPath(program.LOGGING_FILE_PATH) or zb.fileSize(program.LOGGING_FILE_PATH) >= 1024 * 128 else None

dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(levelname)s %(asctime)s %(filename)s %(process)s]:%(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
        },
        "log_file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "default",
            "filename": program.LOGGING_FILE_PATH,
            "encoding": "utf-8",
        },

    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "log_file"],
    },
}
)

logging.info(f"程序启动参数{program.STARTUP_ARGUMENT}!")

program.detectRepeatRun()

logging.info("程序动态数据api初始化成功！")
