import json
import time
import psutil
import platform

import requests
from flask import Flask, jsonify
import flask_cors
import argparse

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser(description='探针服务器')

# 添加 '-r' 或 '--run' 参数，它是一个可选参数
parser.add_argument('-t', '--type', help='运行模式', type=str, default="passive")
parser.add_argument('-i', '--ip', help='主服务地址', type=str, default="127.0.0.1:10088")
parser.add_argument('-n', '--name', help='服务器名称', type=str, default="服务器")

# 解析命令行参数
args = parser.parse_args()

server_type = args.type
home_server = args.ip
server_name = args.name
if not home_server.startswith("http"):
    home_server = "http://" + home_server
# 主动探针
def update():
    # 主动探针请求
    url = f"{home_server}/set_server_list"
    data = json.dumps(get_system_info())
    try:
        print("正在上报服务器数据")
        requests.post(url=url, data={"server_name": server_name, "data": data})
    except Exception as e:
        print(f"请求出错: {e}")


# 被动探针
app = Flask(__name__)
flask_cors.CORS(app, supports_credentials=True)
@app.route('/get_system_info')
def get_system_info():
    return jsonify(get_system_info())


def get_boot_time():
    # 获取开机时间戳
    boot_timestamp = psutil.boot_time()
    boot_time = time.time() - boot_timestamp
    return int(boot_time / 60)


def get_system_info():
    # CPU信息
    # 获取整体CPU使用率
    overall_cpu_usage = psutil.cpu_percent(interval=1)
    # 获取每个核心的CPU使用率
    per_cpu_usage = psutil.cpu_percent(interval=1, percpu=True)

    system_info = {'cpu': {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "frequency": {
            "max": f"{psutil.cpu_freq().max:.2f}Mhz",
            "min": f"{psutil.cpu_freq().min:.2f}Mhz",
            "current": f"{psutil.cpu_freq().current:.2f}Mhz"
        },
        "cpu_usage": {
            "overall_cpu_usage": overall_cpu_usage,
            "per_cpu_usage": per_cpu_usage
        }
    }}

    # 内存信息
    svmem = psutil.virtual_memory()
    system_info['memory'] = {
        "total": f"{svmem.total / (1024 ** 3):.2f} GB",
        "available": f"{svmem.available / (1024 ** 3):.2f} GB",
        "used": f"{svmem.used / (1024 ** 3):.2f} GB",
        "percentage": svmem.percent
    }

    # 磁盘信息
    system_info['disks'] = []
    for partition in psutil.disk_partitions():
        # 忽略/snap目录下的分区
        if partition.mountpoint.startswith("/snap") or partition.mountpoint.startswith("/boot"):
            continue
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        system_info['disks'].append({
            "device": partition.device,
            "mountpoint": partition.mountpoint,
            "total": f"{partition_usage.total / (1024 ** 3):.2f} GB",
            "used": f"{partition_usage.used / (1024 ** 3):.2f} GB",
            "free": f"{partition_usage.free / (1024 ** 3):.2f} GB",
            "percentage": partition_usage.percent
        })

    # 网络信息
    system_info['network'] = {}
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if str(address.family) == 'AddressFamily.AF_INET':
                system_info['network'][interface_name] = {
                    "IP Address": address.address,
                    "Netmask": address.netmask,
                    "Broadcast IP": address.broadcast
                }

    # 操作系统信息
    system_info['os'] = {
        "system": platform.system(),
        "node_name": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "boot_time": get_boot_time(),
    }

    return system_info

# 调用函数并打印结果
info = get_system_info()
print(json.dumps(info, indent=4))

if __name__ == '__main__':
    print(server_type)
    if server_type == "passive":
        app.run("0.0.0.0", 10086)
    elif server_type == "active":
        while True:
            update()
            time.sleep(5)
