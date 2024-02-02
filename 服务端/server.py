import json
import os
import time

import flask
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import make_response

from tools import format_time, config, send_email, save_data
from log import logger

app = flask.Flask(__name__)
# 主动探针服务器列表
with open("server_list.json", "r", encoding="utf-8") as f:
    server_list = json.load(f)
# 被动探针服务器列表
if os.path.exists("cli_server_list.json"):
    with open("cli_server_list.json", "r", encoding="utf-8") as f:
        cli_server_list = json.load(f)
else:
    cli_server_list = []
# 定时请求
scheduler = BackgroundScheduler()

# 定义定时任务
def timed_task():
    logger.info("正在请求服务器数据")
    # 主动探针请求
    for server in server_list:

        try:
            url = f"http://{server['server_ip']}:{server['server_port']}/get_system_info"
            logger.info(f"正在请求 {server['server_name']} 的数据")
            response = requests.get(url=url, timeout=5).json()
            logger.info(f"请求 {server['server_name']} 的数据成功")
            # 格式化时间
            response['os']["boot_time"] = format_time(response['os']["boot_time"])
            # 存储数据
            server["server_info"] = response
            server["server_static"] = "已连接"
            server["update_time"] = time.time()
        except:
            logger.warning(f"请求 {server['server_name']} 的数据失败")
            server["server_info"] = None
            server["server_static"] = "未连接"
            # 判断是否超过设定时间，超过则发送邮件
            update_time = server.get("update_time", 0)
            if time.time() - update_time > 60 * config["setting"]["lostTime"]:
                # 发送邮件
                send_email(config["setting"]["toEmail"], "【探针提醒】服务器掉线", f"服务器<{server['server_name']}>掉线，请及时检查！")
                server["update_time"] = time.time()
    # 被动探针数据处理
    for server in cli_server_list:
        # 判断是否超过设定时间，超过则发送邮件
        update_time = server.get("update_time", 0)
        if time.time() - update_time > 30:
            server["server_static"] = "未连接"
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


# 删除服务器
@app.route('/delete_server')
def delete_server():
    server_ip = flask.request.args.get("server_ip")
    for server in server_list:
        if server["server_ip"] == server_ip:
            server_list.remove(server)
            break
    # 保存数据
    save_data(server_list, "server_list.json")
    return "ok"


@app.route('/get_server_list')
def get_server_list():
    return flask.jsonify(server_list+cli_server_list)


# 接收被动探针数据
@app.route('/set_server_list', methods=["POST"])
def set_server_list():
    server_name = flask.request.form.get("server_name")
    server_ip = flask.request.headers.get('X-Forwarded-For', flask.request.remote_addr)
    server_static = "已连接"
    update_time = time.time()
    server_info = json.loads(flask.request.form.get("data"))
    server_info['os']["boot_time"] = format_time(server_info['os']["boot_time"])

    if server_ip not in [server["server_ip"] for server in cli_server_list]:
        cli_server_list.append({
            "server_name": server_name,
            "server_ip": server_ip,
            "server_static": server_static,
            "update_time": update_time,
            "server_info": server_info
        })
    else:
        for server in cli_server_list:
            if server["server_ip"] == server_ip:
                server["server_name"] = server_name
                server["server_static"] = server_static
                server["update_time"] = update_time
                server["server_info"] = server_info
    # print(cli_server_list)
    return "ok"


# 下载安装脚本
@app.route('/install')
def install():
    run_type = flask.request.args.get("type")
    server_name = flask.request.args.get("name")
    install_path = "static/install_server.sh"
    ip = flask.request.headers.get('X-Forwarded-For', flask.request.remote_addr)
    # 读取安装脚本
    with open(install_path, "r", encoding="utf-8") as fp:
        content = fp.read()
    # 替换变量
    content = content.replace("{{ip}}", f'{config["setting"]["host"]}:{config["setting"]["port"]}')
    # 被动模式
    if run_type == "passive":
        # 第一次请求，添加服务器
        if ip not in [server["server_ip"] for server in server_list]:
            server_list.append({
                "server_name": server_name,
                "server_ip": ip,
                "server_port": 10086,
                "server_static": "已连接",
                "update_time": time.time(),
                "server_info": None
            })
            # 保存数据
            save_data(server_list, "server_list.json")
        content = content.replace("{{run_type}}", f'-t passive')
    # 主动模式
    elif run_type == "active":
        if not server_name:
            return "缺失参数：name", 400
        content = content.replace("{{run_type}}", f'-t active -i {config["setting"]["host"]}:{config["setting"]["port"]} -n {server_name}')
    else:
        return "参数错误：type（passive/active）", 400

    with open("static/install.sh", "w", encoding="utf-8") as fp:
        fp.write(content)
    return flask.send_file("static/install.sh")

if __name__ == '__main__':
    app.run("0.0.0.0", config["setting"]["port"])