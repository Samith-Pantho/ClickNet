from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class DiditIpAnalysesSchema(BaseModel):
    session_id: str = Field(..., alias="session_id")
    browser_family: Optional[str] = Field(None, alias="browser_family")
    device_brand: Optional[str] = Field(None, alias="device_brand")
    device_model: Optional[str] = Field(None, alias="device_model")
    ip_address: Optional[str] = Field(None, alias="ip_address")
    ip_city: Optional[str] = Field(None, alias="ip_city")
    ip_country: Optional[str] = Field(None, alias="ip_country")
    ip_country_code: Optional[str] = Field(None, alias="ip_country_code")
    ip_state: Optional[str] = Field(None, alias="ip_state")
    is_data_center: Optional[bool] = Field(None, alias="is_data_center")
    is_vpn_or_tor: Optional[bool] = Field(None, alias="is_vpn_or_tor")
    isp: Optional[str] = Field(None, alias="isp")
    latitude: Optional[float] = Field(None, alias="latitude")
    longitude: Optional[float] = Field(None, alias="longitude")
    organization: Optional[str] = Field(None, alias="organization")
    os_family: Optional[str] = Field(None, alias="os_family")
    platform: Optional[str] = Field(None, alias="platform")
    status: Optional[str] = Field(None, alias="status")
    time_zone: Optional[str] = Field(None, alias="time_zone")
    time_zone_offset: Optional[str] = Field(None, alias="time_zone_offset")
    warnings: Optional[Dict[str, Any]] = Field(None, alias="warnings")
    locations_info: Optional[Dict[str, Any]] = Field(None, alias="locations_info")

    class Config:
        populate_by_name = True
