import logging


logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
# 创建文件处理器
file_handler = logging.FileHandler('my_log.log')
file_handler.setLevel(logging.ERROR)
# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
# 设置格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
# 添加处理器到日志记录器
logger.addHandler(file_handler)
logger.addHandler(console_handler)