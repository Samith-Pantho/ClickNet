from datetime import datetime
from decimal import Decimal
import traceback
from typing import Optional
from sqlalchemy.sql import text
from Schemas.shared import CustomerRegistrationSchema, SystemLogErrorSchema, AppSettingViewModelSchema
from .LogServices import AddLogOrError

async def sp_get_app_settings_by_keys(conn, keys: str):
    try:
        sql = text("CALL CLICKKYC_GetAppSettingsByKeys(:p_keys)")
        result = await conn.execute(sql, {"p_keys": keys})
        rows = result.fetchall()
        return [AppSettingViewModelSchema(**dict(row._mapping)) for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallClickKycSPServices/sp_get_app_settings_by_keys",
            CreatedBy=""
        ))
        raise Exception(ex)

async def sp_get_all_app_settings(conn):
    try:
        sql = text("CALL CLICKKYC_GetAllAppSettings()")
        result = await conn.execute(sql)
        rows = result.fetchall()
        return [{"KEY": row[0], "VALUE": row[1]} for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallClickKycSPServices/sp_get_all_app_settings",
            CreatedBy=""
        ))
        raise Exception(ex)

async def sp_initialize_tracking_id(conn, phone_number: str, product_code: str) -> str | None:
    try:
        sql = text("CALL CLICKKYC_InitializeTrackingId(:p_phone_number, :p_product_code)")
        result = await conn.execute(sql, {
            "p_phone_number": phone_number,
            "p_product_code": product_code
        })
        row = result.fetchone()
        tracking_id = row.tracking_id if row else None
        print(f"Tracking ID: {tracking_id}")
        return tracking_id

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallClickKycSPServices/sp_initialize_tracking_id",
            CreatedBy=""
        ))
        return None

async def sp_get_tracking_data(conn, tracking_id: str) -> Optional[CustomerRegistrationSchema]:
    try:
        sql = text("CALL CLICKKYC_GetTrackingData(:p_tracking_id)")
        result = await conn.execute(sql, {"p_tracking_id": tracking_id})
        row = result.fetchone()
        
        return CustomerRegistrationSchema(**dict(row._mapping)) if row else None
        
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallClickKycSPServices/sp_get_tracking_data",
            CreatedBy=""
        ))
        raise Exception(ex)

async def sp_update_tracking_data(conn, data: CustomerRegistrationSchema) -> str:
    try:
        sql = text("""
            CALL CLICKKYC_UpdateTrackingData(
                :p_tracking_id, :p_name, :p_title, :p_first_name, :p_middle_name, 
                :p_last_name, :p_suffix, :p_birth_date, :p_tax_id, :p_tax_id_type, :p_is_tax_id_verified,
                :p_address_type, :p_line_1, :p_line_2, :p_line_3, :p_line_4, 
                :p_city, :p_state_code, :p_zipcode, :p_country_code, 
                :p_email_address, :p_phone_number, :p_product_code, 
                :p_branch_code, :p_customer_id, :p_account_number, 
                :p_create_by, :p_status, :p_reject_reason
            ) 
            """)

        result = await conn.execute(sql, {
            "p_tracking_id": data.tracking_id,
            "p_name": data.name,
            "p_title": data.title,
            "p_first_name": data.first_name,
            "p_middle_name": data.middle_name,
            "p_last_name": data.last_name,
            "p_suffix": data.suffix,
            "p_birth_date": data.birth_date,
            "p_tax_id": data.tax_id,
            "p_tax_id_type": data.tax_id_type,
            "p_is_tax_id_verified": data.is_tax_id_verified,
            "p_address_type": data.address_type,
            "p_line_1": data.line_1,
            "p_line_2": data.line_2,
            "p_line_3": data.line_3,
            "p_line_4": data.line_4,
            "p_city": data.city,
            "p_state_code": data.state_code,
            "p_zipcode": data.zipcode,
            "p_country_code": data.country_code,
            "p_email_address": data.email_address,
            "p_phone_number": data.phone_number,
            "p_product_code": data.product_code,
            "p_branch_code": data.branch_code,
            "p_customer_id": data.customer_id,
            "p_account_number": data.account_number,
            "p_create_by": data.create_by,
            "p_status": data.status,
            "p_reject_reason": data.reject_reason
        })

        row = result.fetchone()
        await conn.commit()

        return row.result if row else "UNKNOWN_ERROR"

    except Exception as ex:
        import traceback
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallClickKycSPServices/sp_update_tracking_data",
            CreatedBy=""
        ))
        raise Exception(ex)