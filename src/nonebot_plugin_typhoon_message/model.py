from datetime import datetime

from pydantic import Field, BaseModel, ConfigDict


class BaseDataModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
    )


class GeoPoint(BaseDataModel):
    lat: float | None = None
    lon: float | None = None


class TyphoonCenter(BaseDataModel):
    """WTPQ20 报文台风中心的气象信息"""
    max_wind_speed: float | None = Field(
        default=None,
        description="台风中心附近最大风速，以米／秒 (M/S) 为单位"
    )
    pressure: int | None = Field(
        default=None,
        description="台风的中心气压，以百帕 (HPA) 为单位"
    )


class Movement(BaseDataModel):
    """WTPQ20 报文台风移动数据"""
    speed: float | None = Field(
        default=None,
        description="台风中心移动速度，以公里/小时为单位。"
    )
    speed_description: str | None = Field(
        default=None,
        description="speed字段为None时 此字段可能为 STATIONARY"
    )
    direction: str | None = Field(
        default=None,
        description="台风中心移动方向，以16方位表示。 或为 ALMOST"
    )


class WindRadius(BaseDataModel):
    """
    WTPQ20 报文每个风圈的数据
    风圈在四个方向上的距离, 单位：KM
    """
    northeast: float | None = None
    southeast: float | None = None
    southwest: float | None = None
    northwest: float | None = None


class WindCircle(BaseDataModel):
    """WTPQ20 报文风圈数据"""
    kts30: WindRadius | None = Field(
        default=None,
        description="30节（七级风）大风圈半径，以公里为单位"
    )
    kts50: WindRadius | None = Field(
        default=None,
        description="50节（十级风）大风圈半径，以公里为单位"
    )
    kts64: WindRadius | None = Field(
        default=None,
        description="64节（十二级风）大风圈半径，以公里为单位"
    )


class ForecastCenter(BaseDataModel):
    pressure: int | None = Field(
        default=None,
        description="台风的中心气压，以百帕 (HPA) 为单位"
    )  # 单位：HPA
    max_wind_speed: float | None = Field(
        default=None,
        description="台风中心附近最大风速，以米／秒 (M/S) 为单位"
    )  # 单位：M/S


class ForecastPoint(BaseDataModel):
    """WTPQ20 预报逐小时数据"""
    geo: GeoPoint = Field(default_factory=GeoPoint)
    center: ForecastCenter = Field(default_factory=ForecastCenter)
    level: str | None = None
    level_name: str | None = None


class Forecast(BaseDataModel):
    """WTPQ20 预报数据"""
    hr12: ForecastPoint | None = Field(default=None, alias="+12hr")
    hr24: ForecastPoint | None = Field(default=None, alias="+24hr")
    hr36: ForecastPoint | None = Field(default=None, alias="+36hr")
    hr48: ForecastPoint | None = Field(default=None, alias="+48hr")
    hr60: ForecastPoint | None = Field(default=None, alias="+60hr")
    hr72: ForecastPoint | None = Field(default=None, alias="+72hr")
    hr96: ForecastPoint | None = Field(default=None, alias="+96hr")
    hr120: ForecastPoint | None = Field(default=None, alias="+120hr")


class ReportTime(BaseDataModel):
    raw: str | None = None
    value: datetime | None = None


class MessageMetadata(BaseDataModel):
    msg_id: str
    source: str
    msg_type: str
    msg_name: str | None = None

    received_at_raw: str | None = None
    received_at: datetime | None = None

    web_published_at_raw: str | None = None
    web_published_at: datetime | None = None


class WTPQ20Data(BaseDataModel):
    """WTPQ20 报文数据"""
    agency: str | None = Field(
        default=None,
        description="发报台字母代号 （通常为BABJ国家气象中心）"
    )

    release_time: ReportTime = Field(default_factory=ReportTime)
    initial_time: ReportTime = Field(default_factory=ReportTime)

    level: str | None = Field(
        default=None,
        description="热带气旋等级名称缩写"
    )
    level_name: str | None = None

    name: str | None = Field(
        default=None,
        description="台风的英文命名，未命名时为NAMELESS"
    )
    cn_name: str | None = None

    cma_id: str | None = Field(
        default=None,
        description="国家气象中心的台风编号"
    )
    international_id: str | None = Field(
        default=None,
        description="台风的国际编号"
    )

    geo: GeoPoint = Field(default_factory=GeoPoint)
    movement: Movement = Field(default_factory=Movement)
    center: TyphoonCenter = Field(default_factory=TyphoonCenter)

    wind_circle: WindCircle = Field(default_factory=WindCircle)
    forecast: Forecast = Field(default_factory=Forecast)


class TCPQ40Intensity(BaseDataModel):
    """台风强度信息"""
    change_24h: str | None = Field(
        default=None,
        description="24小时内台风强度的明显变化 (at) 见 INTENSITY_CHANGE_DESCRIPTION",
    )
    ci: float | str | None = Field(
        default=None,
        description="台风现时强度（CI）指数。float型时为CI值，str型时见 CI_DESCRIPTION",
    )


class TCPQ40Movement(BaseDataModel):
    """TCPQ40 报文移动组"""
    calculate_interval: str | None = Field(
        default=None,
        description="计算台风的移动的时间间隔 (tm)",
    )
    direction: str | None = Field(
        default=None,
        description="使用数字表示的台风移向，精度为10° 若不报移动组，本字段为None",
    )
    speed: int | None = Field(
        default=None,
        description="台风移速，单位：节(Kt) 若不报移动组，本字段为None",
    )


class TCPQ40Typhoon(BaseDataModel):
    """TCPQ40 报文台风信息"""
    name: str | None = Field(
        default=None,
        description="台风英文名称",
    )
    cn_name: str | None = Field(
        default=None,
        description="台风中文名称",
    )
    serial: str | None = Field(
        default=None,
        description="台风序号 (ntnt) 通常情况下与台风编号的后两位相同",
    )
    geo: GeoPoint = Field(default_factory=GeoPoint)
    location_accuracy: str | None = Field(
        default=None,
        description="台风地理位置定位的精确度 (At) 见 LOCATION_ACCURACY_DESCRIPTION",
    )
    cdo: str | None = Field(
        default=None,
        description="台风密蔽云区的平均直径 (Wf)",
    )
    intensity: TCPQ40Intensity = Field(default_factory=TCPQ40Intensity)
    movement: TCPQ40Movement = Field(default_factory=TCPQ40Movement)


class TCPQ40Data(BaseDataModel):
    """TCPQ40 报文数据"""
    agency: str | None = Field(
        default=None,
        description="发报台字母代号 （通常为BABJ国家气象中心）"
    )
    release_time: ReportTime = Field(default_factory=ReportTime)
    report_code: str | None = Field(
        default=None,
        description=("前半部分 陆地测站用 `CC` 作为标志，海洋测站用 `DD` 作为标志"
                     "后边部分 `AA` 为`台风的情报`， `BB` 为 `重要天气特征的情报`"
                     "此项通常为 CCAA 固定值"),
    )
    photo_time: ReportTime = Field(
        default_factory=ReportTime,
        description="气旋照片拍摄时间（通常与发报时间相同）"
    )
    station_location: GeoPoint = Field(
        default_factory=GeoPoint,
        description="编报本报告的卫星接收站的位置（通常为固定值）"
    )

    typhoons: list[TCPQ40Typhoon] = Field(default_factory=list)


class TyphoonMessage(BaseDataModel):
    schema_version: int = 1

    metadata: MessageMetadata
    ty_data: WTPQ20Data | TCPQ40Data

    raw_msg: list[str] = Field(default_factory=list)
