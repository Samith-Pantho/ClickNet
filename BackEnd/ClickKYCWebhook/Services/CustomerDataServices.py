import json
import traceback
from typing import Any
from datetime import datetime
from pydantic import BaseModel
from Schemas.shared import CustomerRegistrationSchema, DiditVerificationViewModelSchema, SystemLogErrorSchema
from Services.CommonServices import ApiCall, ConvertToBool
from Services.KYCServices import GetTrackingData, UpdateTrackingData
from Services.LogServices import AddLogOrError


async def UpdateCustomerRegistrationData(verification_data: DiditVerificationViewModelSchema) -> CustomerRegistrationSchema:
    try:
        existingdata = await GetTrackingData(verification_data.vendor_data)
        if not existingdata:
            raise ValueError(f"No data found for tracking id - {verification_data.vendor_data}")
        
        def GetData(obj, *attrs):
            for attr in attrs:
                obj = getattr(obj, attr, None)
                if obj is None:
                    return None
            return obj

        id_verif = GetData(verification_data, 'decision', 'id_verification')
        ip_analysis = GetData(verification_data, 'decision', 'ip_analysis')

        existingdata.name = GetData(id_verif, 'full_name')
        existingdata.title = None
        existingdata.first_name = GetData(id_verif, 'first_name')
        existingdata.middle_name = None
        existingdata.last_name = GetData(id_verif, 'last_name')
        existingdata.suffix = None

        dob_str = GetData(id_verif, 'date_of_birth')
        if dob_str:
            birth_date = datetime.fromisoformat(dob_str)
            existingdata.birth_date = birth_date.date()
        else:
            existingdata.birth_date = None

        existingdata.tax_id = GetData(id_verif, 'document_number')
        existingdata.tax_id_type = GetData(id_verif, 'document_type')
        existingdata.is_tax_id_verified = (verification_data.status == "Approved") if verification_data and verification_data.status else None
        existingdata.verification_session_id = getattr(verification_data, 'session_id', None)
        if existingdata.is_tax_id_verified == False:
            existingdata.status = "REJECTED"
            existingdata.reject_reason = await _GetVerificationFailedReason(verification_data)

        latitude = GetData(ip_analysis, 'latitude')
        longitude = GetData(ip_analysis, 'longitude')
        
        if latitude and longitude:
            addressDataUsingGeoLoation = await _ReverseGeocodeOSM(latitude, longitude)
            address = addressDataUsingGeoLoation.get('address', {})
            line_1 = ""
            if 'house_number' in address and 'road' in address:
                line_1 = f"{address.get('house_number', '')} {address.get('road', '')}".strip()
            elif 'road' in address:
                line_1 = address.get('road', '')
            
            line_2 = address.get('suburb', '') or address.get('neighbourhood', '')
            line_3 = address.get('city_district', '')
            line_4 = ''
            
            city = address.get('city', '') or address.get('town', '') or address.get('village', '')
            state_code = address.get('state', '')
            zipcode = address.get('postcode', '')
            country_code = address.get('country_code', '').upper()
            
            existingdata.address_type = "Current Address"
            existingdata.line_1 = line_1
            existingdata.line_2 = line_2
            existingdata.line_3 = line_3
            existingdata.line_4 = line_4
            existingdata.city = city
            existingdata.state_code = state_code
            existingdata.zipcode = zipcode
            existingdata.country_code = country_code
        
        result = await UpdateTrackingData(existingdata)
        await AddLogOrError(SystemLogErrorSchema(
            Msg="Update CustomerRegistration Data with Didit Data Successfully - "f"{verification_data.session_id}",
            Type = "LOG",
            ModuleName = "CustomerDataServices/UpdateCustomerRegistrationData",
            CreatedBy = ""
        ))
              
        return await GetTrackingData(existingdata.tracking_id)
        
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CustomerDataServices/UpdateCustomerRegistrationData",
            CreatedBy = verification_data.vendor_data
        ))
        raise Exception(ex)
    
    
async def _GetVerificationFailedReason(data: DiditVerificationViewModelSchema, separator: str = "\n") -> str:
    
    try:
        descriptions = []
        if not data.decision:
            return ""

        # Mapping features to their corresponding decision sub-model
        feature_map = {
            "IDVERIFICATION": "id_verification",
            "ID_VERIFICATION": "id_verification",
            "FACEMATCH": "face_match",
            "FACE_MATCH": "face_match",
            "LIVENESS": "liveness",
            "IPANALYSIS": "ip_analysis",
            "IP_ANALYSIS": "ip_analysis",
        }

        for feature_key, sub_model_name in feature_map.items():
            sub_model = getattr(data.decision, sub_model_name, None)
            if sub_model and getattr(sub_model, "warnings", None):
                for warning in sub_model.warnings:
                    if warning.long_description:
                        descriptions.append(warning.long_description)

        return separator.join(descriptions)

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CustomerDataServices/GetVerificationFailedReason",
            CreatedBy = ""
        ))
        raise Exception(ex)

async def _ReverseGeocodeOSM(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'format': 'json',
            'lat': lat,
            'lon': lon,
            'addressdetails': 1,
            'zoom': 18,
            'accept-language': 'en'
        }
        headers = {
            'User-Agent': 'MyApp (myemail@example.com)'
        }
        
        data = await ApiCall(
            method="GET",
            url=url,
            headers=headers,
            params=params
        )
        return data
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CustomerDataServices/ReverseGeocodeOSM",
            CreatedBy = ""
        ))
        raise Exception(ex)