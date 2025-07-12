from Config.dbConnection import conn
from Models.shared import appSettings


def FetchAppSettingsByKey(key: str):
    try:
        appSetting = conn.execute(appSettings.select().where(appSettings.c.KEY == key.upper())).first()
        if appSetting:
            return appSetting.VALUE
        else:
            return None
    except Exception as ex:
        return None