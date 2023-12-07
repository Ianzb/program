import random
import threading
import time
import urllib.request
import json
import hashlib
import os
import warnings

from beta.source.custom import *

SERVER_IP = "124.221.74.246"
PORT = 82
APP_ID = ""
APP_KEY = os.environ.get('PYCHAT_APP_KEY')
PROTOCOL = "http"


class ChatAPI:
    def __init__(self, server_ip=None, port=None, app_id=None, app_key=None):
        self.server_ip = server_ip if server_ip else SERVER_IP
        self.port = port if port else PORT
        self.app_id = app_id if app_id else APP_ID
        self.app_key = app_key if app_key else APP_KEY
        self.connected = False
        self.username = ""
        self.session = ""
        self.exception_stack = []

    def _gen_salt(self):
        return str(random.randint(1, 100000))

    def _get_sign(self, *args, **kwargs):
        sign_str = self.app_id + self.app_key
        for i in args:
            sign_str += i
        return hashlib.sha256(sign_str.encode()).hexdigest()

    def _send_request(self, api_name, data):
        url = f"{PROTOCOL}://{self.server_ip}:{self.port}/api/v1/{api_name}"
        headers = {'Content-Type': 'application/json'}
        json_data = json.dumps(data).encode('utf8')
        req = urllib.request.Request(url=url, data=json_data, headers=headers)
        response = urllib.request.urlopen(req)
        result = response.read().decode('utf8')
        return json.loads(result)

    def _handle_exception(self, data):
        warnings.showwarning(f"ChatAPI警告：{data['err_no']}: {data['err_info']}", UserWarning, 'chatapi.py', 0)
        self.exception_stack.append({
            'err_no': data['err_no'],
            'err_info': data['err_info']
        })

    def register_user(self, username, password, description=""):
        salt = self._gen_salt()
        result = self._send_request(
            api_name="register_user",
            data={
                'app_id': self.app_id,
                'username': username,
                'password': password,
                'description': description,
                'salt': salt,
                'sign': self._get_sign(username, password, description, salt)
            }
        )
        if result['status'] == 0:
            pass
        else:
            self._handle_exception(result)

    def login_user(self, username, password, heartbeat_interval=60):  # 设置heartbeat间隔，默认为60s，设置为-1禁用heartbeat
        salt = self._gen_salt()
        result = self._send_request(
            api_name="login_user",
            data={
                'app_id': self.app_id,
                'username': username,
                'password': password,
                'salt': salt,
                'sign': self._get_sign(username, password, salt)
            }
        )
        if result['status'] == 0:
            self.connected = True
            self.username = username
            self.session = result['session']
            if heartbeat_interval > 0:
                threading.Thread(target=lambda: self.start_heartbeat(heartbeat_interval), daemon=True).start()
        else:
            self._handle_exception(result)

    def start_heartbeat(self, heartbeat_interval):
        while self.connected:
            self.heartbeat()
            time.sleep(heartbeat_interval)

    def heartbeat(self):
        salt = self._gen_salt()
        result = self._send_request(
            api_name="heartbeat",
            data={
                'app_id': self.app_id,
                'session': self.session,
                'salt': salt,
                'sign': self._get_sign(self.session, salt)
            }
        )
        if result['status'] == 0:
            pass
        else:
            self._handle_exception(result)

    def get_user_info(self, username):
        salt = self._gen_salt()
        result = self._send_request(
            api_name="get_user_info",
            data={
                'app_id': self.app_id,
                'session': self.session,
                'username': username,
                'salt': salt,
                'sign': self._get_sign(self.session, username, salt)
            }
        )
        if result['status'] == 0:
            return result
        else:
            self._handle_exception(result)


if __name__ == '__main__':
    api_test = ChatAPI(
        server_ip='127.0.0.1',
        port=5000,
        app_id='MZFiLAzmJu',
        app_key='vUCiKf167oNUfpdbsxKs'
    )
    api_test.login_user("apitest", "idk", heartbeat_interval=5)
    print(api_test.get_user_info(api_test.username))
    print(api_test.get_user_info('test'))
    time.sleep(100)


