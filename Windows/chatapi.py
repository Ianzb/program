import random
import urllib.request
import json
import hashlib
import os

SERVER_IP = "124.221.74.246"
PORT = 82
APP_ID = ""
APP_KEY = os.environ.get('PYCHAT_APP_KEY')


class ChatAPI:
    def __init__(self, server_ip=None, port=None, app_id=None, app_key = None):
        self.server_ip = server_ip if server_ip else SERVER_IP
        self.port = port if port else PORT
        self.app_id = app_id if app_id else APP_ID
        self.app_key = app_key if app_key else APP_KEY

    def _gen_salt(self):
        return str(random.randint(1, 100000))

    def _get_sign(self, *args, **kwargs):
        sign_str = self.app_id + self.app_key
        for i in args:
            sign_str += i
        return hashlib.sha256(sign_str.encode()).hexdigest()

    def _send_requset(self, url, data):
        headers = {'Content-Type': 'application/json'}
        json_data = json.dumps(data).encode('utf8')
        req = urllib.request.Request(url=url, data=json_data, headers=headers)
        response = urllib.request.urlopen(req)
        result = response.read().decode('utf8')
        return result

    def register_user(self, username, password, description=""):
        salt = self._gen_salt()
        return self._send_requset(
            url=f"http://{self.server_ip}:{self.port}/api/v1/register_user",
            data={
                'app_id': self.app_id,
                'username': username,
                'password': password,
                'description': description,
                'salt': salt,
                'sign': self._get_sign(username, password, description, salt)
            }
        )


if __name__ == '__main__':
    api_test = ChatAPI(
        server_ip='127.0.0.1',
        port=5000,
        app_id='MZFiLAzmJu',
        app_key='vUCiKf167oNUfpdbsxKs'
    )
    api_test.register_user('apitest', 'idk', 'Hey!')

