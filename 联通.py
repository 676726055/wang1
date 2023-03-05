import logging
import os
import sys
import traceback
import requests

logging.basicConfig(level=logging.INFO, format='%(message)s')

env_key = "LT_COOKIE"


def load_send() -> None:
    logging.info("加载推送功能中...")
    global send
    send = None
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/notify.py"):
        try:
            from notify import send
        except Exception:
            send = None
            logging.info(f"❌加载通知服务失败!!!\n{traceback.format_exc()}")
    else:
        logging.info(f"❌加载通知服务失败!!!\n")


def get_envs(env_key):
    if env_key in os.environ:
        configs = os.environ[env_key]
        if len(configs) > 0:
            try:
                return configs
            except Exception as e:
                logging.error(f"{env_key}变量格式错误: {e}")
                sys.exit(1)

        else:
            logging.info(f"{env_key}变量量未启用")
            sys.exit(1)
    else:
        logging.info(f'未添加{env_key}变量')
        sys.exit(1)


def get_from_cookie(ck, key):
    phone = ''
    kvs = ck.split(";")
    for kv in kvs:
        split = kv.split("=")
        if split[0] == key:
            phone = split[1]
            break
    return phone


class Unicom(object):
    def __init__(self, cookie):
        self.cookie = cookie
        self.ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 unicom{version:iphone_c@10.0200}'
        self.is_valid = False
        self.phone = get_from_cookie(self.cookie, 'c_mobile')
        self.nickname = ''
        self.all_msg = []

    def get_info(self):
        try:
            info_res = requests.get(
                url="https://m.client.10010.com/mobileService/customer/query/getMyUnicomDateTotle.htm",
                headers={
                    "Cookie": self.cookie,
                    "User-Agent": self.ua
                }
            ).json()
        except Exception:
            return

        # 响应中有nickName就视为获取信息成功
        if info_res['nickName']:
            self.is_valid = True
            self.phone = info_res['phone']
            self.nickname = info_res['nickName']
        else:
            if not self.phone:
                self.phone = '从cookie中未获取到手机号'

    # 签到 (我的 - 右上角签到)
    def day_sign(self):
        sign_res = requests.get(
            url="https://act.10010.com/SigninApp/signin/daySign",
            headers={
                "Cookie": self.cookie,
                "User-Agent": self.ua,
            }
        ).json()
        if sign_res['status'] == '0000':
            msg = f'🎁每日签到: {sign_res["data"]["signMessage"]}'
        else:
            msg = f'❌每日签到: {sign_res["msg"]}'

        self.all_msg.append(msg)

    def main(self):
        self.get_info()
        if not self.is_valid and not self.phone:
            self.phone = '从cookie中未获取到手机号'

        self.all_msg.append(f'===== {self.phone} =====')
        if self.is_valid:
            # 签到
            self.day_sign()
            # 其他...

        logging.info('\n'.join(self.all_msg))


if __name__ == '__main__':
    # 加载通知
    load_send()

    cookies = get_envs(env_key)
    all_log = []
    for ck in cookies.split("&"):
        u = Unicom(ck)
        u.main()

        # 拼所有日志用于通知
        all_log += u.all_msg
        all_log.append("\n")

    # 通知
    send("联通任务", '\n'.join(all_log))
