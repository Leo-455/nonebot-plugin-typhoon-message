from nonebot import logger

from .model import TCPQ40Data, WindRadius, WTPQ20Data, ForecastPoint, TCPQ40Typhoon
from .utils import parse_geo, current_time, extract_number, timezone_convert
from .constants import (
    TY_NAME,
    TY_LV_NAME,
    CI_DESCRIPTION,
    CDO_DESCRIPTION,
    CN_TELEGRAM_CODE,
    INTENSITY_CHANGE_DESCRIPTION,
    LOCATION_ACCURACY_DESCRIPTION,
    MV_CACULATE_TIMEDELTA_DESCRIPTION,
)


def handle_wtpq20(ty_msg: list[str]) -> WTPQ20Data:
    ty_data = WTPQ20Data()
    for i, line in enumerate(ty_msg):  # 逐行处理
        line = line.strip()  # 去除首尾空格
        words = line.split()  # 按空格分隔

        if line == "NNNN":  # 报尾
            break

        if i == 0:  # 检查报文是否完整
            if line != "ZCZC":
                logger.error("电文错误 未找到报头")
        elif i == 1:
            if words[0] != "WTPQ20":
                logger.error(f"报文类型错误：应为WTPQ20 实为{words[0]}")
            ty_data.agency = words[1]
            ty_data.release_time.raw = words[2] # TODO 

        elif "INITIAL TIME" in line:  # 台风信息
            level = words[0]  # 强度等级
            ty_data.level = level
            ty_data.level_name = TY_LV_NAME.get(level)

            name = words[1]
            ty_data.name = name
            if name.isdigit():  # 未命名热带低压 名字为数字 没有编号
                ty_data.initial_time.raw = words[4]
            else:  # 已命名
                ty_data.initial_time.raw = words[6]
                ty_data.cma_id = words[2]  # 国内编号
                ty_data.international_id = words[3].strip("()")
                ty_data.cn_name = TY_NAME.get(name.title())  # 台风名称

        elif "00HR" in line:  # 台风实况
            if words[0] == "00HR":
                ty_data.geo.lat = parse_geo(words[1])
                ty_data.geo.lon = parse_geo(words[2])
                pressure = extract_number(words[3])
                ty_data.center.pressure = (
                    int(pressure) if pressure is not None else None
                )  # 中心气压
                wind_speed = extract_number(words[4])
                ty_data.center.max_wind_speed = (
                    int(wind_speed) if wind_speed is not None else None
                )  # 中心风速

        elif "WINDS" in line:  # 风圈半径信息
            wind_speed = extract_number(words[0])
            if wind_speed is not None:
                wind_speed = int(wind_speed)

                # if wind_speed not in {30, 50, 64}:
                #     raise TyphoonParseError(f"未知风圈类型：{wind_speed}KTS")

                field_name = f"kts{wind_speed}"
                wind_radius = getattr(ty_data.wind_circle, field_name)

                if wind_radius is None:
                    wind_radius = WindRadius()
                    setattr(ty_data.wind_circle, field_name, wind_radius)

                wind_radius.northeast = extract_number(words[2])
                wind_radius.southeast = extract_number(ty_msg[i + 1].split()[0])
                wind_radius.southwest = extract_number(ty_msg[i + 2].split()[0])
                wind_radius.northwest = extract_number(ty_msg[i + 3].split()[0])

        elif "MOVE" in line:  # 移速信息
            ty_data.movement.direction = words[1] # 移向可能为"ALMOST" 意为 "原地少动"

            mv_speed = words[2].replace("=", "")
            if mv_speed == "STATIONARY":
                ty_data.movement.speed_description = mv_speed
            else:
                ty_data.movement.speed = extract_number(mv_speed)

        elif "P+" in line:  # 预报信息
            hour_shift = extract_number(words[0])
            if hour_shift is not None:
                hour_shift = int(hour_shift)

                # if hour_shift not in {12, 24, 36, 48, 60, 72, 96, 120}:
                #     raise TyphoonParseError(f"未知预报时效：{hour_shift}HR")

                field_name = f"hr{hour_shift}"
                forecast_point = getattr(ty_data.forecast, field_name)
                if forecast_point is None:
                    forecast_point = ForecastPoint()
                    setattr(ty_data.forecast, field_name, forecast_point)

                forecast_point.geo.lat = parse_geo(words[1])
                forecast_point.geo.lon = parse_geo(words[2])

                forecast_pressure = extract_number(words[3])
                forecast_point.center.pressure = (
                    int(forecast_pressure)
                    if forecast_pressure is not None
                    else None
                )

                forecast_wind_speed = extract_number(words[4].replace("=", ""))
                forecast_point.center.max_wind_speed = forecast_wind_speed

                forecast_level = get_typhoon_level(forecast_wind_speed)
                forecast_point.level = forecast_level
                forecast_point.level_name = (
                    TY_LV_NAME.get(forecast_level)
                    if forecast_level is not None
                    else None
                )

    return ty_data


def handle_tcpq40(ty_msg: list[str]) -> TCPQ40Data:
    ty_data = TCPQ40Data()
    for i, line in enumerate(ty_msg):
        line = line.strip()
        words = line.split()

        if line == "NNNN":  # 报尾
            break

        if i == 0:  # 检查报文是否完整
            if line != "ZCZC":
                logger.error("CMA TY MSG | 电文错误 未找到报头")
        elif i == 1:
            if words[0] != "TCPQ40":
                logger.error(f"报文类型错误：应为TCPQ40 实为{words[0]}")
            ty_data.agency = words[1]
            ty_data.release_time.raw = words[2]
        elif i == 2:
            # if words[0] == "CCAA":
            #     title = "陆地测站关于台风的情报"
            # elif words[0] == "CCBB":
            #     title = "陆地测站关于重要天气特征的情报"
            # elif words[0] == "DDAA":
            #     title = "海洋测站关于台风的情报"
            # elif words[0] == "DDBB":
            #     title = "海洋测站关于重要天气特征的情报"
            # else:
            #     title = ""
            ty_data.report_code = words[0]
            ty_data.photo_time.raw = words[1]
            lat = words[2]
            if lat.startswith("99"):
                ty_data.station_location.lat = int(lat[2:]) / 10
            lon = words[3]
            # earth_quadrant = lon[1]
            ty_data.station_location.lon = int(lon[1:]) / 10

        elif i > 2:  # 第3行之后每行是一个台风信息
            typhoons = TCPQ40Typhoon()
            typhoons.name = words[0]
            typhoons.cn_name = TY_NAME.get(words[0].title())

            typhoons.serial = words[1][:2]
            typhoons.geo.lat = int(words[1][2:]) / 10

            # earth_quadrant = words[2][0]  # Qc
            typhoons.geo.lon = int(words[2][1:]) / 10

            if words[3].startswith("1"):
                typhoons.location_accuracy = (
                    LOCATION_ACCURACY_DESCRIPTION.get(words[3][1])
                    )
                typhoons.cdo = CDO_DESCRIPTION.get(words[3][2])
                typhoons.intensity.change_24h = (
                    INTENSITY_CHANGE_DESCRIPTION.get(words[3][3])
                )
                typhoons.movement.calculate_interval = (
                    MV_CACULATE_TIMEDELTA_DESCRIPTION.get(words[3][4])
                )

            if words[4].startswith("2") and words[4].endswith("//"):
                ci = CI_DESCRIPTION.get(words[4][1:3])
                if ci is not None:
                    typhoons.intensity.ci = ci
                else:
                    typhoons.intensity.ci = int(words[4][1:3]) /10

            if len(words) == 6 and words[5].startswith("9"):
                mv_direction = words[5][1:3]
                if mv_direction == "00":
                    typhoons.movement.direction = "静止"
                elif mv_direction == "//":
                    typhoons.movement.direction = None
                else:
                    typhoons.movement.direction = f"{mv_direction}0"

                mv_speed = words[5][-2:]
                if mv_speed == "//":
                    typhoons.movement.speed = None
                else:
                    mv_speed = extract_number(mv_speed)
                    typhoons.movement.speed = (
                        int(mv_speed) if mv_speed is not None else None
                    )
            ty_data.typhoons.append(typhoons)

    return ty_data


# def handle_whci40(ty_msg: list):
#     for i, line in enumerate(ty_msg):
#         line = line.strip()
#         words = line.split()

#         if line == "NNNN":  # 报尾
#             break

#         if i == 0:  # 检查报文是否完整
#             if line != "ZCZC":
#                 logger.error("CMA TY MSG | 电文错误 未找到报头")
#         elif i == 1:
#             real_time = timezone_convert(
#                 f"{utc_year}{words[2]}",
#                 "UTC",
#                 input_time_format="%Y%d%H%M",
#                 output_time_format="%d日%H时",
#             )
#         elif i == 2:
#             level = TY_LV_NAME.get(words[0])  # 强度等级

#             try:
#                 name = TY_NAME[words[3].title()]  # 台风名称
#             except KeyError:
#                 name = words[3]

#             ty_id = words[1]
#             landed_location = ""
#             for j in words[6:]:
#                 landed_location += str(j) + " "
#         elif i == 3:
#             center_windspeed = re.search(
#                 r"\((.*?)\)", words[-1]
#             )  # 正则表达式，匹配括号中的内容
#             center_windspeed = (
#                 center_windspeed.group(1) if center_windspeed is not None else None
#             )


# def handle_wsci40(ty_msg: list):
#     utc_year = timezone_convert(
#         current_time(), "Asia/Shanghai", "UTC", "%Y/%m/%d %H:%M:%S", "%Y"
#     )
#     for i, line in enumerate(ty_msg):
#         line = line.strip()
#         words = line.split()
#         if line == "NNNN":  # 报尾
#             break

#         if i == 0:  # 检查报头
#             if line != "ZCZC":
#                 logger.error("CMA TY MSG | 电文错误 未找到报头")
#         elif i == 1:
#             real_time = timezone_convert(
#                 f"{utc_year}{words[-1]}",
#                 "UTC",
#                 input_time_format="%Y%d%H%M",
#                 output_time_format="%d日%H时",
#             )
#             output = f"CMA台风报文\n发报时间：{real_time}\n"
#         elif i >= 2:
#             # 四位数字为中文电报码，码表存储在bot_resources_data.json中
#             for word in words:
#                 if word.isdigit():  # 如果全部是数字 直接进行解码
#                     output += CN_TELEGRAM_CODE.get(word)

#                 # 如果里面有括号 括号内的内容是需要保留的数字 不进行解码
#                 # 有两种情况
#                 # 情况一：只有括号(nnnn) 直接去掉括号即可
#                 # 情况二：xxxx(nnnn)xxxx 整体会被分为一个word 需要提取数字
#                 # 然后分别解码两边的电码
#                 elif "(" in word or ")" in word:
#                     # 提取括号中的内容
#                     digit_in_brackets = re.search(r"\((.*?)\)", word)
#                     digit_in_brackets = (
#                         digit_in_brackets.group(1)
#                         if digit_in_brackets is not None
#                         else ""
#                     )

#                     # 将括号及括号内的内容替换为一个空格
#                     word = re.sub(r"\(.*?\)", " ", word)

#                     # 进行分割 情况一只有一个空格啥也分割不出来 结果为空列表
#                     # 情况二是能分割出两个的
#                     word = word.split()
#                     if word != []:
#                         output += CN_TELEGRAM_CODE.get(word[0])
#                         output += digit_in_brackets
#                         output += CN_TELEGRAM_CODE.get(word[-1])
#                     elif word == []:
#                         output += digit_in_brackets

#                 # 有BABJ直接结束 (第一个BABJ在前两行已经过去了)
#                 elif "BABJ" in word:
#                     break

#                 # TO XXXX的情况
#                 else:
#                     output += f"{word} "


def get_typhoon_level(wind_speed: float | None) -> str | None:
    """根据风速判断热带气旋等级，单位：m/s。"""
    if wind_speed is None:
        return None
    elif wind_speed < 10.8:
        return ""
    elif wind_speed < 17.2:
        return "TD"
    elif wind_speed < 24.5:
        return "TS"
    elif wind_speed < 32.7:
        return "STS"
    elif wind_speed < 41.5:
        return "TY"
    elif wind_speed < 51.0:
        return "STY"
    elif wind_speed >= 51.0:
        return "SuperTY"
    else:
        return None
