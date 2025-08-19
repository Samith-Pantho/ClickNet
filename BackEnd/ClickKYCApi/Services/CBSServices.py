from datetime import datetime
import traceback
from Config.dbConnection import AsyncSessionLocalCBS
from sqlalchemy.ext.asyncio import AsyncSession
from .LogServices import AddLogOrError

from Schemas.shared import SystemLogErrorSchema, CustomerRegistrationSchema

from .CallCBSSPServices import sp_create_customer, sp_get_products_for_kyc, sp_get_branch_list, sp_get_customer_by_id, sp_check_customer_for_product, sp_open_account

async def GetProductsForKyc(product_category: str):
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_products_for_kyc(db_session, product_category)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetProductsForKyc",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()
            
async def GetBranchList():
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_branch_list(db_session)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetBranchList",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()
            
async def GetCustomerbyID(id: str):
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_get_customer_by_id(db_session, id)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/GetCustomerbyID",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def CheckCustomerForProduct(id: str,product_code: str):
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_check_customer_for_product(db_session, id, product_code)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/CheckCustomerForProduct",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()
            
async def CreateCustomer(data: CustomerRegistrationSchema):
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_create_customer(db_session, data)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/CreateCustomer",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()

async def CreateAccount(data: CustomerRegistrationSchema):
    db_session = None
    try:
        db_session = AsyncSessionLocalCBS()
        return await sp_open_account(db_session, data)
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "CBSServices/CreateAccount",
            CreatedBy = ""
        ))
        return None
    finally:
        if db_session:
            await db_session.close()