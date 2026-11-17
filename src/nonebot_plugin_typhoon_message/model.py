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
    max_wind_speed: float | None = None
    pressure: int | None = None


class Movement(BaseDataModel):
    speed: float | None = None
    speed_description: str | None = None
    direction: str | None = None


class WindRadius(BaseDataModel):
    """风圈在四个方向上的距离, 单位：KM"""
    northeast: float | None = None
    southeast: float | None = None
    southwest: float | None = None
    northwest: float | None = None


class WindCircle(BaseDataModel):
    kts30: WindRadius | None = None
    kts50: WindRadius | None = None
    kts64: WindRadius | None = None


class ForecastCenter(BaseDataModel):
    pressure: int | None = None  # 单位：HPA
    max_wind_speed: float | None = None  # 单位：M/S


class ForecastPoint(BaseDataModel):
    geo: GeoPoint = Field(default_factory=GeoPoint)
    center: ForecastCenter = Field(default_factory=ForecastCenter)
    level: str | None = None
    level_name: str | None = None


class Forecast(BaseDataModel):
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
    agency: str | None = None

    release_time: ReportTime = Field(default_factory=ReportTime)
    initial_time: ReportTime = Field(default_factory=ReportTime)

    level: str | None = None
    level_name: str | None = None

    name: str | None = None
    cn_name: str | None = None

    cma_id: str | None = None
    international_id: str | None = None

    geo: GeoPoint = Field(default_factory=GeoPoint)
    movement: Movement = Field(default_factory=Movement)
    center: TyphoonCenter = Field(default_factory=TyphoonCenter)

    wind_circle: WindCircle = Field(default_factory=WindCircle)
    forecast: Forecast = Field(default_factory=Forecast)


class TyphoonMessage(BaseDataModel):
    schema_version: int = 1

    metadata: MessageMetadata
    ty_data: WTPQ20Data | TCPQ40Data

    raw_msg: list[str] = Field(default_factory=list)
