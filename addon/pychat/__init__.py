import hashlib
import json
import random

from source.addon import *

try:
    from program.source.addon import *
except:
    pass
addonBase = AddonBase()


def addonInit():
    global program, log, setting, window, api
    program = addonBase.program
    log = addonBase.log
    setting = addonBase.setting
    window = addonBase.window
    api = PyChatApi()


def addonWidget():
    return AddonPage(window)


class PyChatApi:
    BASE_URL = "http://localhost:5000"
    HEADER = {"Content-Type": "application/json"}
    APPID = program.STARTUP_ARGUMENT[program.STARTUP_ARGUMENT.index("--pychatappid") + 1]
    APPKEY = program.STARTUP_ARGUMENT[program.STARTUP_ARGUMENT.index("--pychatappkey") + 1]

    def getAppId(self):
        return self.APPID

    def getAppKey(self):
        return self.APPKEY

    def _genSalt(self):
        return str(random.randint(1, 100000))

    def _genSignStr(self, *args, **kwargs):
        return hashlib.sha256((self.getAppId() + self.getAppKey() + "".join(args)).encode()).hexdigest()

    def loginUser(self, username, password):
        salt = self._genSalt()
        data = {
            "app_id": self.getAppId(),
            "username": username,
            "password": password,
            "salt": salt,
            "sign": self._genSignStr(username, password, salt)
        }
        response = f.postUrl(f.joinUrl(self.BASE_URL, "/api/v1/login_user"), data, self.HEADER)
        return json.load(response.text)


class LoginPage(BasicTab):
    loginSignal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMaximumWidth(500)
        self.setMinimumSize(400, 400)
        self.setStyleSheet("QLabel{\n"
                           "    font: 13px \'Microsoft YaHei\'\n"
                           "}")

        self.vBoxLayout = VBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(9)

        self.lineEdit1 = LineEdit(self)
        self.lineEdit1.setPlaceholderText("ftp.example.com")
        self.lineEdit1.setClearButtonEnabled(True)

        self.label1 = BodyLabel(self)
        self.label1.setText("主机")

        self.lineEdit2 = LineEdit(self)
        self.lineEdit2.setPlaceholderText("")
        self.lineEdit2.setClearButtonEnabled(True)
        self.lineEdit2.setText("21")

        self.label2 = BodyLabel(self)
        self.label2.setText("端口")

        self.gridLayout = QGridLayout()
        self.gridLayout.setHorizontalSpacing(4)
        self.gridLayout.setVerticalSpacing(9)
        self.gridLayout.addWidget(self.lineEdit1, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.label1, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.lineEdit2, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.label2, 0, 1, 1, 1)
        self.gridLayout.setColumnStretch(0, 2)
        self.gridLayout.setColumnStretch(1, 1)
        self.vBoxLayout.addLayout(self.gridLayout)

        self.label3 = BodyLabel(self)
        self.label3.setText("用户名")

        self.lineEdit3 = LineEdit(self)
        self.lineEdit3.setPlaceholderText("example@example.com")
        self.lineEdit3.setClearButtonEnabled(True)

        self.label4 = BodyLabel(self)
        self.label4.setText("密码")

        self.lineEdit4 = LineEdit(self)
        self.lineEdit4.setPlaceholderText("••••••••••••")
        self.lineEdit4.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit4.setClearButtonEnabled(True)

        self.checkBox = CheckBox(self)
        self.checkBox.setText("记住密码")
        self.checkBox.setChecked(True)

        self.pushButton1 = PrimaryPushButton(self)
        self.pushButton1.setText("登录")
        setToolTip(self.pushButton1, "登录账户")
        self.pushButton1.clicked.connect(lambda: program.THREAD_POOL.submit(self.login))

        self.pushButton2 = HyperlinkButton(self)
        self.pushButton2.setText("找回密码")

        self.vBoxLayout.addWidget(self.label3)
        self.vBoxLayout.addWidget(self.lineEdit3)
        self.vBoxLayout.addWidget(self.label4)
        self.vBoxLayout.addWidget(self.lineEdit4)
        self.vBoxLayout.addItem(QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))
        self.vBoxLayout.addWidget(self.checkBox)
        self.vBoxLayout.addItem(QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))
        self.vBoxLayout.addWidget(self.pushButton1)
        self.vBoxLayout.addItem(QtWidgets.QSpacerItem(20, 6, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))
        self.vBoxLayout.addWidget(self.pushButton2)
        self.vBoxLayout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        self.loginSignal.connect(self.loginFinished)

    def login(self):
        try:
            data = api.loginUser(self.lineEdit3.text(), self.lineEdit4.text())
            self.loginSignal.emit(data)
        except Exception as ex:
            log.error(f"登录错误，报错信息：{ex}！")

    def loginFinished(self, data):
        print(data)


class AddonPage(ChangeableTab):
    """
    插件主页面
    """
    signalList = pyqtSignal(list)
    signalBool = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.CHAT)
        print(api.getAppId())
        self.addPage(LoginPage(self), "PyChat", Qt.AlignCenter)
        self.showPage("PyChat")
