import json
from pathlib import Path

from nonebot import logger

WEBPAGE_URL = "https://www.nmc.cn/publish/typhoon/message.html"

MSG_BASE_URL = "https://nmc.cn/f/rest/getContent?dataId="

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0"
}

TY_LV_NAME = {
    "": "残余涡旋",
    "TD": "热带低压",
    "TS": "热带风暴",
    "STS": "强热带风暴",
    "TY": "台风",
    "STY": "强台风",
    "SuperTY": "超强台风",
}
"""台风级别描述"""

MV_CACULATE_TIMEDELTA_DESCRIPTION = {
    "0": "<１小时",
    "1": "1～<2小时",
    "2": "2～<3小时",
    "3": "3～<6小时",
    "4": "6～<9小时",
    "5": "9～<12小时",
    "6": "12～<15小时",
    "7": "15～<18小时",
    "8": "18～<21小时",
    "9": "21～<30小时",
    "/": "不报移动组",
}
"""计算台风移动的时间间隔描述"""

LOCATION_ACCURACY_DESCRIPTION = {
    "0": "10公里以内",
    "1": "20公里以内",
    "2": "50公里以内",
    "3": "100公里以内",
    "4": "200公里以内",
    "5": "300公里以内",
    "/": "不明",
}
"""台风定位精度描述"""

CDO_DESCRIPTION = {
    "0": "<1个纬距",
    "1": "1～<2个纬距",
    "2": "2～<3个纬距",
    "3": "3～<4个纬距",
    "4": "4～<5个纬距",
    "5": "5～<6个纬距",
    "6": "6～<7个纬距",
    "7": "7～<8个纬距",
    "8": "8～<9个纬距",
    "/": "不明",
}
"""CDO平均直径描述"""

INTENSITY_CHANGE_DESCRIPTION = {
    "0": "很明显减弱",
    "1": "明显减弱",
    "2": "无明显变化",
    "3": "明显加强",
    "4": "很明显加强",
    "9": "先前没有观测",
    "/": "不明",
}
"""强度变化描述"""

CI_DESCRIPTION = {"00": "衰减", "99": "向温带气旋转变", "//": "不明"}
"""CI值描述"""


resources_data_path = Path(__file__).parent / "bot_resources_data.json"
try:
    with open(resources_data_path, 'r', encoding='utf-8') as file:
        resources_data = json.load(file)
        TY_NAME: dict = resources_data["ty_name"]
        CN_TELEGRAM_CODE: dict = resources_data["cn_telegram_code"]
        data_update_time = resources_data["UpdateTime"]
        logger.success(f"数据文件读取成功，更新时间{data_update_time}")
except Exception as e:
    raise RuntimeError("未找到数据文件或数据文件损坏") from e

