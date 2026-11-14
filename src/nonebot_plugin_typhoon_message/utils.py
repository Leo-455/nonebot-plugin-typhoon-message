import re
import time
from datetime import datetime

import pytz


def timezone_convert(time: str, input_timezone: str,
                     target_timezone: str = "Asia/Shanghai",
                     input_time_format: str = "%Y/%m/%d %H:%M:%S",
                     output_time_format: str = "%Y/%m/%d %H:%M:%S") -> str:
    """
    转换输入时间的时区

    Args:
        time: 要转换的时间
        input_timezone: 输入时间的时区, 格式为pytz时区名称
        target_timezone: 输出时间的时区, 格式为pytz时区名称, 默认为北京时间
        input_time_format: 输入时间的格式 注意：如果输入时间不包括年，可能导致出现几分钟的偏差
        output_time_format: 输出时间的格式

    Returns:
        time: 转换完成的时间
    """
    target_pytz_timezone = pytz.timezone(target_timezone)  # 设置目标时区
    timezone = pytz.timezone(input_timezone)  # 转换为 pytz 时区对象
    date_time = datetime.strptime(time, input_time_format)  # 将字符串提取为时间
    date_time = timezone.localize(date_time).astimezone(target_pytz_timezone)  # 时区转换
    output_time = date_time.strftime(output_time_format)  # 格式化 2024-11-20 23:09:09
    return output_time


def current_time(output_time_format: str = "%Y/%m/%d %H:%M:%S") -> str:
    """
    获取当前时间

    Args:
        output_time_format: 输出时间的格式

    Returns:
        t: 当前时间
    """
    t = time.strftime(output_time_format, time.localtime())
    return t


def extract_number(value: str) -> float | None:
    """提取字符串中的数值"""
    match = re.search(r"-?\d+(?:\.\d+)?", value)

    if match is None:
        return None

    return float(match.group())


def parse_geo(value: str) -> float | None:
    """将带方向的经纬度转换为十进制度。"""
    number = extract_number(value)

    if number is None:
        return None

    if value.endswith(("S", "W")):
        return -number

    return number
