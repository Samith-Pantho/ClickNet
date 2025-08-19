from datetime import datetime
import json
import traceback
from sqlalchemy import text
from .LogServices import AddLogOrError
from Schemas.shared import SystemLogErrorSchema, ProductViewModelSchema, BranchViewModelSchema, CustomerRegistrationSchema

# 1. Fetch products for KYC
async def sp_get_products_for_kyc(conn, product_category: str):
    try:
        sql = text("CALL CBS_GetProductsForKyc(:p_product_category)")
        result = await conn.execute(sql, {"p_product_category": product_category})
        rows = result.fetchall()
        return [ProductViewModelSchema(**dict(row._mapping)) for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallSPServices/sp_get_products_for_kyc",
            CreatedBy=""
        ))
        raise Exception(ex)

# 2. Fetch branch list
async def sp_get_branch_list(conn):
    try:
        sql = text("CALL CBS_GetBranchList()")
        result = await conn.execute(sql)
        rows = result.fetchall()
        return [BranchViewModelSchema(**dict(row._mapping)) for row in rows]
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallSPServices/sp_get_branch_list",
            CreatedBy=""
        ))
        raise Exception(ex)

# 3. Get customer ID by tax ID
async def sp_get_customer_by_id(conn, tax_id: str) -> str:
    try:
        result = await conn.execute(
            text("CALL CBS_GetCustomerById(:tax_id, @p_customer_id)"),
            {"tax_id": tax_id}
        )
        
        # Fetch the OUT parameter
        out_param = await conn.execute(text("SELECT @p_customer_id"))
        customer_id = out_param.scalar()
        return str(customer_id) if customer_id else ""
        
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallSPServices/sp_get_customer_by_id",
            CreatedBy=""
        ))
        raise

# 3. Get customer ID by tax ID & product code
async def sp_check_customer_for_product(conn, tax_id: str, product_code: str) -> str:
    try:
        # For MySQL stored procedures with OUT parameters
        await conn.execute(
            text("CALL CBS_CheckCustomerForProduct(:tax_id, :product_code, @p_customer_id)"),
            {"tax_id": tax_id, "product_code": product_code}
        )
        
        # Fetch the OUT parameter
        out_param = await conn.execute(text("SELECT @p_customer_id"))
        customer_id = out_param.scalar()
        return str(customer_id) if customer_id else ""
        
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="CallSPServices/sp_check_customer_for_product",
            CreatedBy=""
        ))
        raise
    
# 5. Create customer
async def sp_create_customer(conn, data: CustomerRegistrationSchema):
    try:
        sql = text("""
            CALL CBS_CreateCustomer(
                :p_type, :p_name, :p_title, :p_first_name, :p_middle_name, 
                :p_last_name, :p_suffix, :p_birth_date, :p_formation_date, 
                :p_tax_id, :p_tax_id_type, :p_branch_code,
                :p_address_type, :p_line_1, :p_line_2, :p_line_3, :p_line_4,
                :p_city, :p_state_code, :p_zipcode, :p_country_code,
                :p_email_type, :p_email_address,
                :p_phone_type, :p_phone_number
            )
        """)
        
        params = {
            "p_type": "INDIVIDUAL",
            "p_name": data.name,
            "p_title": data.title,
            "p_first_name": data.first_name,
            "p_middle_name": data.middle_name,
            "p_last_name": data.last_name,
            "p_suffix": data.suffix,
            "p_birth_date": data.birth_date,
            "p_formation_date": datetime.now(),
            "p_tax_id": data.tax_id,
            "p_tax_id_type": data.tax_id_type,
            "p_branch_code": data.branch_code,
            "p_address_type": data.address_type,
            "p_line_1": data.line_1,
            "p_line_2": data.line_2,
            "p_line_3": data.line_3,
            "p_line_4": data.line_4,
            "p_city": data.city,
            "p_state_code": data.state_code,
            "p_zipcode": data.zipcode,
            "p_country_code": data.country_code,
            "p_email_type": "PRIMARY",
            "p_email_address": data.email_address,
            "p_phone_type": "PRIMARY",
            "p_phone_number": data.phone_number
        }
        
        result = await conn.execute(sql, params)
        await conn.commit()
        row = result.fetchone()
        data.customer_id = row[0] 
        
        await AddLogOrError(
            SystemLogErrorSchema(
                Msg="New Customer ID Created Successfully",
                Type="LOG",
                ModuleName="CallSPServices/sp_create_customer",
                CreatedBy=data.tracking_id
            )
        )
        return data
        
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(
            SystemLogErrorSchema(
                Msg=error_msg,
                Type="ERROR",
                ModuleName="CallSPServices/sp_create_customer",
                CreatedBy=data.tracking_id
            )
        )
        raise

# 6. Open account
async def sp_open_account(conn, data: CustomerRegistrationSchema):
    try:
        sql = text("""
            CALL CBS_OpenAccount(
                :p_customer_id, 
                :p_product_code
            )
        """)
        
        params = {
            "p_customer_id": data.customer_id,
            "p_product_code": data.product_code
        }
        
        result = await conn.execute(sql, params)
        await conn.commit()
        row = result.fetchone()
        data.account_number = row[0] 
        
        print(f"Account-{data.account_number}")
        await AddLogOrError(
            SystemLogErrorSchema(
                Msg="New Account created Successfully",
                Type="LOG",
                ModuleName="CallSPServices/sp_open_account",
                CreatedBy=data.tracking_id
            )
        )
        return data
        
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(
            SystemLogErrorSchema(
                Msg=error_msg,
                Type="ERROR",
                ModuleName="CallSPServices/sp_open_account",
                CreatedBy=data.tracking_id
            )
        )
        raise
