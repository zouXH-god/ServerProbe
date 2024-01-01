import json
import time

import flask
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from tools import format_time, config, send_email

app = flask.Flask(__name__)
with open("server_list.json", "r", encoding="utf-8") as f:
    server_list = json.load(f)
# 定时请求
scheduler = BackgroundScheduler()

# 定义定时任务
def timed_task():
    for server in server_list:
        url = f"http://{server['server_ip']}:{server['server_port']}/get_system_info"
        try:
            response = requests.get(url=url).json()
            # 格式化时间
            response['os']["boot_time"] = format_time(response['os']["boot_time"])
            # 存储数据
            server["server_info"] = response
            server["server_static"] = "已连接"
            server["update_time"] = time.time()
        except:
            server["server_info"] = None
            server["server_static"] = "未连接"
            # 判断是否超过设定时间，超过则发送邮件
            update_time = server.get("update_time", 0)
            if time.time() - update_time > 60 * config["setting"]["lostTime"]:
                # 发送邮件
                send_email(config["setting"]["toEmail"], "【探针提醒】服务器掉线", f"服务器<{server['server_name']}>掉线，请及时检查！")
                server["update_time"] = time.time()

# 添加定时任务，间隔5秒
scheduler.add_job(timed_task, 'interval', seconds=5)
scheduler.start()
timed_task()


@app.route('/')
def index():
    index_path = "static/index/index.html"
    return open(index_path, "r", encoding="utf-8").read()


@app.route('/get_server_list')
def get_server_list():
    return flask.jsonify(server_list)


if __name__ == '__main__':
    app.run("0.0.0.0", 10088)