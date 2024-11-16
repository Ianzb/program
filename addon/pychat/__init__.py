import hashlib
import random
import time

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
    PyChatApi.APPID = program.STARTUP_ARGUMENT[program.STARTUP_ARGUMENT.index("--pychatappid") + 1]
    PyChatApi.APPKEY = program.STARTUP_ARGUMENT[program.STARTUP_ARGUMENT.index("--pychatappkey") + 1]


def addonWidget():
    return AddonPage(window)


class PyChatApiSession:
    def __init__(self, session: str, exp_time: float):
        self.session: str = session
        self.exp_time: float = exp_time  # timestamp

    @property
    def is_valid(self):
        return self.session is not None and self.exp_time is not None and self.exp_time > time.time()

    def getSession(self):
        return self.session

    def setSession(self, session):
        self.session = session

    def getExpTime(self):
        return self.exp_time

    def setExpTime(self, exp_time):
        self.exp_time = exp_time


class PyChatApiSessionManager:
    def __init__(self):
        self.sessions = {}  # {username: PyChatApiSession}

    def getSession(self, username):
        self.sessions.get(username)

    def addOrUpdateSession(self, username, session, exp_time):
        self.sessions.update({username: PyChatApiSession(session, exp_time)})
        program.THREAD_POOL.submit(self.heartbeat)

    def clearSession(self):
        self.sessions.clear()

    def heartbeat(self):
        while True:
            time.sleep(250)
            for session in self.sessions.values():
                log.info(f"已自动更新Session{session.getSession()}！")
                api.heartbeat(session)


sessionManager = PyChatApiSessionManager()


class PyChatApi:
    BASE_URL = "localhost:5000"
    HEADER = {"Content-Type": "application/json"}
    APPID = None
    APPKEY = None

    @classmethod
    def getUrl(cls):
        return "http://" + cls.BASE_URL

    def setUrl(self, ip, port):
        ip.lstrip("https://").lstrip("http://")
        self.BASE_URL = ip + ":" + port

    @staticmethod
    def api(relative_path, arguments_seq, callback=None):
        """
        api默认装饰器，以简化api编写
        回调示例：callback(data_dict, response_obj)
        """

        def decorator(func):
            @functools.wraps(func)  # 使用 wraps 来保留原函数的元数据
            def wrapper(*args, **kwargs):
                salt = PyChatApi._genSalt()
                data_dict: dict = func(*args, **kwargs)
                arguments_values = [data_dict[a] for a in arguments_seq] + [salt]
                sign = PyChatApi._genSignStr(*arguments_values)
                data_dict.setdefault("app_id", PyChatApi.getAppId())
                data_dict.setdefault("salt", salt)
                data_dict.setdefault("sign", sign)
                response = f.postUrl(f.joinUrl(PyChatApi.getUrl(), relative_path), data_dict, PyChatApi.HEADER)
                response_obj = response.json()

                if callback:
                    callback(data_dict, response_obj)

                return {"data_dict": data_dict, "response_obj": response_obj}

            return wrapper

        return decorator

    @classmethod
    def getAppId(cls):
        return cls.APPID

    @classmethod
    def getAppKey(cls):
        return cls.APPKEY

    @staticmethod
    def _genSalt():
        return str(random.randint(1, 100000))

    @classmethod
    def _genSignStr(cls, *args):
        return hashlib.sha256((cls.getAppId() + cls.getAppKey() + "".join(args)).encode()).hexdigest()

    @api("/api/v1/login_user", ["username", "password"], callback=lambda data_dict, response_obj: PyChatApi.postLoginUser(data_dict, response_obj))  # TODO: add callback function to store session
    def loginUser(self, username, password):
        return {
            "username": username,
            "password": password,
        }

    @staticmethod
    def postLoginUser(data_dict: dict, response_obj: dict):
        status = response_obj.get("status", -1)
        if status == 0:
            session = data_dict.get("session", None)
            if session is not None:
                sessionManager.addOrUpdateSession(data_dict.get("username"), session, data_dict.get("exp_time"))
                return response_obj
        else:
            log.error(f"登录失败，{data_dict}, {response_obj}")

    @api("/api/v1/register_user", ["username", "password", "description"])
    def registerUser(self, username, password, description=""):
        return {
            'username': username,
            'password': password,
            'description': description
        }

    @api("api/v1/heartbeat", ["session"])
    def heartbeat(self, session):
        return {
            'session': session.getSession()
        }


class LoginPage(BasicTab):
    loginSignal = pyqtSignal(dict)
    successSignal = pyqtSignal()
    errorSignal = pyqtSignal()

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
        self.lineEdit1.setText(api.BASE_URL.split(":")[0])
        self.lineEdit1.setPlaceholderText("ftp.example.com")
        self.lineEdit1.setClearButtonEnabled(True)

        self.label1 = BodyLabel(self)
        self.label1.setText("主机")

        self.lineEdit2 = LineEdit(self)
        self.lineEdit2.setText(api.BASE_URL.split(":")[1])
        self.lineEdit2.setPlaceholderText("0")
        self.lineEdit2.setClearButtonEnabled(True)

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
        self.vBoxLayout.addItem(
            QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))
        self.vBoxLayout.addWidget(self.checkBox)
        self.vBoxLayout.addItem(
            QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))
        self.vBoxLayout.addWidget(self.pushButton1)
        self.vBoxLayout.addItem(
            QtWidgets.QSpacerItem(20, 6, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))
        self.vBoxLayout.addWidget(self.pushButton2)
        self.vBoxLayout.addItem(
            QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        self.loginSignal.connect(self.loginFinished)
        self.successSignal.connect(self.loginSuccess)
        self.errorSignal.connect(self.loginError)

    def loginSuccess(self):
        InfoBar(InfoBarIcon.SUCCESS, "提示", "登录成功！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent()).show()

    def loginError(self):
        InfoBar(InfoBarIcon.ERROR, "错误", "登录失败！", Qt.Orientation.Vertical, True, 5000, InfoBarPosition.TOP_RIGHT, self.parent()).show()

    def login(self):
        if not self.lineEdit3.text() or not self.lineEdit4.text(): return
        self.pushButton1.setText("加载中...")
        self.pushButton1.setEnabled(False)
        try:
            api.setUrl(self.lineEdit1.text(), self.lineEdit2.text())
            data = api.loginUser(self.lineEdit3.text(), self.lineEdit4.text())
            if data["response_obj"]["status"] < 0:
                raise KeyError(f"Login Error {data["response_obj"]["err_info"]}")
            self.loginSignal.emit(data)
            self.successSignal.emit()
            log.info(f"登录成功，登录信息为：{data}！")
        except Exception as ex:
            self.errorSignal.emit()
            log.error(f"登录错误，报错信息：{ex}！")
        self.pushButton1.setText("登录")
        self.pushButton1.setEnabled(True)

    def loginFinished(self, data):
        self.parent().showPage("Chat")
        self.parent().page["Chat"].setUser(data)


class ChatToolBar(QWidget):
    """ Tool bar """

    def __init__(self, title, parent=None):
        super().__init__(parent=parent)
        self.titleLabel = TitleLabel(title, self)
        # self.subtitleLabel = CaptionLabel(subtitle, self)

        self.loginButton = PushButton("登录", self, FIF.PEOPLE)

        self.vBoxLayout = QVBoxLayout(self)
        self.buttonLayout = QHBoxLayout()

        self.__initWidget()

    def __initWidget(self):
        self.setFixedHeight(100)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(36, 22, 36, 12)
        # self.vBoxLayout.addWidget(self.titleLabel)
        # self.vBoxLayout.addSpacing(4)
        # self.vBoxLayout.addWidget(self.subtitleLabel)
        self.vBoxLayout.addSpacing(4)
        self.vBoxLayout.addLayout(self.buttonLayout, 1)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.buttonLayout.setSpacing(4)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.addWidget(self.titleLabel, 0, Qt.AlignLeft)
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.loginButton, 0, Qt.AlignRight)
        self.buttonLayout.addStretch(1)
        self.buttonLayout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)


class ChatPage(BasicTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.toolBar = ChatToolBar("未登录", self)

        self.setViewportMargins(0, self.toolBar.height(), 0, 0)

        self.toolBar.loginButton.clicked.connect(lambda: self.parent().showPage("PyChat"))

        self.user: dict | None = None

    def setUser(self, data: dict):
        self.user = data["data_dict"]
        self.toolBar.titleLabel.setText(self.user["username"])


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
        self.addPage(ChatPage(self), "Chat")
        self.showPage("Chat")
