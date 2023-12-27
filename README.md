# ServerProbe

## 概述
服务器探针项目是一个基于Python的监控工具，可实时提供CPU使用率、内存、磁盘使用情况、网络详细信息及操作系统信息等多种系统资源信息。该项目采用客户端-服务器架构，客户端负责收集系统数据，服务器端则负责检索和显示这些信息。
![e12e326dae95df01ef7c0372bc551e69](https://github.com/zouXH-god/ServerProbe/assets/77649130/c2bf3a42-a6f7-42d5-9a7a-4187fe3008f8)

## 系统要求
- Python 3.x
- Flask
- psutil
- platform
- flask_cors
- requests
- apscheduler

## 安装
1. 克隆仓库：
   ```
   git clone https://github.com/zouXH-god/ServerProbe.git
   ```
2. 安装依赖项：
   ```
   pip install Flask psutil flask_cors requests apscheduler
   ```

## 服务端安装
服务器定期从客户端获取系统信息，并显示这些信息。

1. 进入服务端目录。
2. 配置server_list.json文件，添加客户端信息
   ```
   {
    "server_name": "客户端服务器名称",
    "server_ip": "111.111.111.111(客户端服务器ip)",
    "server_port": "10086(客户端使用端口——默认为10086)",
    "server_static": "未连接",
    "server_info": null
   }
   ```
4. 运行脚本：
   ```
   python server.py
   ```
5. 服务器在端口10088上启动，可以在 `http://IP:10088` 访问。

## 客户端安装
客户端脚本收集系统信息，并通过Flask API暴露这些信息。

在服务器端安装完成后，可直接通过指令下载并启动安装客户端

1. 新建一个客户端存放目录，并进入。
2. 执行：
   ```
   wget -N http://IP:10088/static/install_server.sh && bash ./install_server.sh
   ```
3. 客户端在端口10086上启动。

## 使用方法
1. 访问服务器的Web界面，查看已连接客户端及其系统状态。
2. 每5秒从客户端获取实时数据。

## 客户端API端点
- `/get_system_info`：返回包括CPU、内存、磁盘、网络和操作系统数据在内的详细系统信息。

## 服务器API端点
- `/`：主仪表板，显示已连接的客户端。
- `/get_server_list`：返回所有已连接服务器的列表及其状态和详细信息。

## 配置
- `server_list.json`：添加或修改客户端服务器列表及其IP和端口。

## 贡献
欢迎贡献。请fork仓库，进行更改，并提交pull request。

## 许可证
[请在此处指定许可证]

## 联系方式
欢迎加群：876873473

## 致谢
- 感谢Flask提供轻量级Web服务器框架。
- 感谢psutil提供高效的系统监控能力。
- 感谢Python社区持续的支持和贡献。
