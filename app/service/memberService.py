import random
import string
import hashlib
from flask import current_app
import requests


#随机字符串
class memberService():

    @staticmethod
    def geneAuthCode(member=None):
        m = hashlib.md5()
        str = "%s-%s-%s" % (member.id, member.salt, member.status)
        m.update(str.encode("utf-8"))
        return m.hexdigest()

    @staticmethod
    def getOpenid(code):
        app_id = current_app.config.get('APP_ID')
        app_secret = current_app.config.get('APP_SECRET')
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'.format(
            app_id, app_secret, code)
        print(url)
        response = requests.get(url)
        content = response.json()
        print(content.get('openid'), 'www')
        open_id = content.get('openid')

        return open_id

    @staticmethod
    def getSalt(len=16):
        str = [random.choice(string.ascii_letters + string.digits) for _ in range(1, len + 1)]

        ran_str = "".join(str)

        return ran_str
