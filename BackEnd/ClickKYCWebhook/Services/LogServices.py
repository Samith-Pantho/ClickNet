import os
from datetime import datetime
from Config.dbConnection import AsyncSessionLocalClickKyc
from sqlalchemy.ext.asyncio import AsyncSession
from Cache.AppSettingsCache import Get
from Models.shared import systemLogError
from Schemas.shared import SystemLogErrorSchema

async def  AddLogOrError(data: SystemLogErrorSchema):
    AddLogOrErrorInFileOrDb = Get("ADD_LOG_IN_FILE_OR_DB")
    if  AddLogOrErrorInFileOrDb and AddLogOrErrorInFileOrDb.upper() ==  "FILE":
        await AddLogOrErrorInFile(data.Msg, data.Type)
    elif AddLogOrErrorInFileOrDb and AddLogOrErrorInFileOrDb.upper() ==  "DB":
        await AddLogOrErrorInDB(data)
    else:
        return None

async def  AddLogOrErrorInFile(message: str, type: str):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = (
            f"{timestamp} <======> {type} <======> {message}\n\n"
            f"{'*' * 100}\n\n"
        )

        # Build path
        log_dir = "/app/logs" #os.path.join("C:\\", "Clicknet.Log")
        os.makedirs(log_dir, exist_ok=True)

        # Log file name based on date
        log_filename = f"ClickKycWebHook - {datetime.now().strftime('%d-%m-%Y')}.txt"
        log_path = os.path.join(log_dir, log_filename)

        # Append log message
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_message)
    except Exception as ex:
        print(f"Logging failed: {ex}")
        
async def  AddLogOrErrorInDB(data: SystemLogErrorSchema):
    db_session = None
    try:
        db_session = AsyncSessionLocalClickKyc()
        write_log = False

        if data.Type == "ERROR":
            write_log = True
        else:
            setting = Get("IS_ENABLE_LOG_INSERT")
            write_log = str(setting).lower() == "true"

        if write_log:
            if len(data.Msg) > 4000:
                AddLogOrErrorInFile(data.Msg, type)
                data.Msg = data.Msg[:3999]

            insert_stmt = systemLogError.insert().values(
                ERR_DT=datetime.now(),
                ERR_TYPE=data.Type,
                ERR_MSG=data.Msg,
                MODULE_NAME=data.ModuleName,
                CREATED_BY=data.CreatedBy.lower()
            )

            await db_session.execute(insert_stmt)
            await db_session.commit()

    except Exception as ex:
        await AddLogOrErrorInFile(f"DB Exception Error: {str(ex)}\nOriginal Message: {data.Msg}", "ERROR")