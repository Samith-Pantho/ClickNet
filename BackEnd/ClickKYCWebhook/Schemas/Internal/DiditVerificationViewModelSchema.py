from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class WarningModel(BaseModel):
    additional_data: Optional[Any]
    feature: Optional[str]
    log_type: Optional[str]
    long_description: Optional[str]
    risk: Optional[str]
    short_description: Optional[str]


class DistanceModel(BaseModel):
    direction: Optional[str]
    distance: Optional[float]


class LocationModel(BaseModel):
    latitude: Optional[float]
    longitude: Optional[float]


class DocumentLocationInfo(BaseModel):
    distance_from_ip: Optional[DistanceModel]
    distance_from_poa_document: Optional[Any]
    location: Optional[LocationModel]


class IPDistanceInfo(BaseModel):
    distance_from_id_document: Optional[DistanceModel]
    distance_from_poa_document: Optional[Any]
    location: Optional[LocationModel]


class LocationsInfoModel(BaseModel):
    id_document: Optional[DocumentLocationInfo]
    ip: Optional[IPDistanceInfo]
    poa_document: Optional[Any]


class IPAnalysisModel(BaseModel):
    browser_family: Optional[str]
    device_brand: Optional[str]
    device_model: Optional[str]
    ip_address: Optional[str]
    ip_city: Optional[str]
    ip_country: Optional[str]
    ip_country_code: Optional[str]
    ip_state: Optional[str]
    is_data_center: Optional[bool]
    is_vpn_or_tor: Optional[bool]
    isp: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    locations_info: Optional[LocationsInfoModel]
    organization: Optional[str]
    os_family: Optional[str]
    platform: Optional[str]
    status: Optional[str]
    time_zone: Optional[str]
    time_zone_offset: Optional[str]
    warnings: Optional[List[WarningModel]] = [] 


class FaceMatchModel(BaseModel):
    score: Optional[float]
    source_image: Optional[str]
    source_image_session_id: Optional[str]
    status: Optional[str]
    target_image: Optional[str]
    warnings: Optional[List[WarningModel]] = [] 


class IDVerificationModel(BaseModel):
    address: Optional[str]
    age: Optional[int]
    back_image: Optional[str]
    back_video: Optional[str]
    date_of_birth: Optional[str]
    date_of_issue: Optional[str]
    document_number: Optional[str]
    document_type: Optional[str]
    expiration_date: Optional[str]
    extra_fields: Optional[Dict[str, Any]]
    extra_files: Optional[List[Any]]
    first_name: Optional[str]
    formatted_address: Optional[str]
    front_image: Optional[str]
    front_video: Optional[str]
    full_back_image: Optional[str]
    full_front_image: Optional[str]
    full_name: Optional[str]
    gender: Optional[str]
    issuing_state: Optional[str]
    issuing_state_name: Optional[str]
    last_name: Optional[str]
    marital_status: Optional[str]
    nationality: Optional[str]
    parsed_address: Optional[Any]
    personal_number: Optional[str]
    place_of_birth: Optional[str]
    portrait_image: Optional[str]
    status: Optional[str]
    warnings: Optional[List[WarningModel]] = [] 


class LivenessModel(BaseModel):
    age_estimation: Optional[float]
    method: Optional[str]
    reference_image: Optional[str]
    score: Optional[float]
    status: Optional[str]
    video_url: Optional[str]
    warnings: Optional[List[WarningModel]] = [] 


class DecisionModel(BaseModel):
    aml: Optional[Any]
    callback: Optional[str]
    contact_details: Optional[Any]
    created_at: Optional[str]
    database_validation: Optional[Any]
    expected_details: Optional[Any]
    face_match: Optional[FaceMatchModel]
    features: Optional[List[str]]
    id_verification: Optional[IDVerificationModel]
    ip_analysis: Optional[IPAnalysisModel]
    liveness: Optional[LivenessModel]
    metadata: Optional[Any]
    nfc: Optional[Any]
    phone: Optional[Any]
    poa: Optional[Any]
    reviews: Optional[List[Any]]
    session_id: Optional[str]
    session_number: Optional[int]
    session_url: Optional[str]
    status: Optional[str]
    vendor_data: Optional[str]
    workflow_id: Optional[str]


class DiditVerificationViewModelSchema(BaseModel):
    created_at: Optional[int]
    decision: Optional[DecisionModel]
    session_id: Optional[str]
    status: Optional[str]
    timestamp: Optional[int]
    vendor_data: Optional[str]
    workflow_id: Optional[str]
