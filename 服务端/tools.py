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

