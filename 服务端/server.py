import json

import flask
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from tools import format_time

app = flask.Flask(__name__)
with open("server_list.json", "r", encoding="utf-8") as f:
    server_list = json.load(f)
# 定时请求
scheduler = BackgroundScheduler()


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
        except:
            server["server_info"] = None
            server["server_static"] = "未连接"

# 添加定时任务，间隔5秒
scheduler.add_job(timed_task, 'interval', seconds=5)
scheduler.start()


@app.route('/')
def index():
    index_path = "static/index/index.html"
    return open(index_path, "r", encoding="utf-8").read()


@app.route('/get_server_list')
def get_server_list():
    return flask.jsonify(server_list)


if __name__ == '__main__':
    app.run("0.0.0.0", 10088)