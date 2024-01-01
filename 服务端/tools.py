import json
import os

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header


root_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(root_path, "setting.json")
with open(config_path, "r", encoding="utf-8") as fp:
    config = json.load(fp)


def format_time(minutes):
    # 定义时间单位
    minutes_per_hour = 60
    minutes_per_day = 24 * minutes_per_hour

    # 计算天数、小时数和剩余分钟数
    days = minutes // minutes_per_day
    hours = (minutes % minutes_per_day) // minutes_per_hour
    remaining_minutes = minutes % minutes_per_hour

    # 根据时间的大小构建输出字符串
    if days > 0:
        return f"{days}天{hours}时{remaining_minutes}分"
    elif hours > 0:
        return f"{hours}时{remaining_minutes}分"
    else:
        return f"{remaining_minutes}分"


# 发送邮件
def send_email(to_addr, subject, content):
    """
    发送电子邮件。

    :param to_addr: 收件人地址
    :param subject: 邮件主题
    :param content: 邮件内容
    :return: None
    """

    # 第三方 SMTP 服务
    mail_host = config["email"]["smtp"]  # 设置服务器
    mail_port = config["email"]["port"]  # 设置服务器端口号
    mail_user = config["email"]["email"]  # 用户名
    mail_pass = config["email"]["password"]  # 口令
    receivers = [to_addr]  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    # 创建一个 MIMEText 对象，指定邮件正文和 MIME 类型
    message = MIMEMultipart()
    message['From'] = mail_user
    message['To'] = to_addr
    message['Subject'] = subject

    html = MIMEText(content, 'html', 'utf-8')
    message.attach(html)
    try:
        # 使用 SSL 创建 SMTP 对象
        smtp_obj = smtplib.SMTP_SSL(mail_host, mail_port)
        smtp_obj.login(mail_user, mail_pass)  # 登录
        smtp_obj.sendmail(mail_user, receivers, message.as_string())  # 发送邮件
        smtp_obj.quit()  # 关闭连接
    except smtplib.SMTPException as e:
        print("Error: 无法发送邮件", e)


if __name__ == '__main__':
    send_email('2488252513@qq.com', "subject", "content")