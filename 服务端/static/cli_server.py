import json
from datetime import datetime
import time
import psutil
import platform
from flask import Flask, jsonify
import flask_cors

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
    app.run("0.0.0.0", 10086)
