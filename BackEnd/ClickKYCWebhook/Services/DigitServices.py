import os
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import time
from io import BytesIO
from PIL import Image
from fastapi import requests
import httpx
from sqlalchemy import and_, func, select
from Models.shared import diditSessions, diditDecisions, diditFaceMatches, diditIdVerifications, diditIpAnalyses, diditLiveness, diditWarnings
from Schemas.shared import SystemLogErrorSchema, DiditSessionsSchema, DiditDecisionsSchema, DiditFaceMatchesSchema, DiditIdVerificationsSchema, DiditIpAnalysesSchema, DiditLivenessSchema, DiditWarningsSchema, DiditVerificationViewModelSchema, WarningModel, DistanceModel, LocationModel, DocumentLocationInfo, IPDistanceInfo, LocationsInfoModel, IPAnalysisModel, FaceMatchModel, IDVerificationModel, LivenessModel, DecisionModel, StatusResult
from Config.dbConnection import AsyncSessionLocalClickKyc
from sqlalchemy.ext.asyncio import AsyncSession
from Services.CommonServices import ApiCall, EncryptImage, GetErrorMessage, GetSha1Hash
from Services.GenericCRUDServices import GenericInserter, GenericUpdater
from .LogServices import AddLogOrError
from Cache.AppSettingsCache import Get

async def CreateDiditSession(data: Dict[str, Any]):
    status = StatusResult()
    try:
        url = "https://verification.didit.me/v2/session/"
        headers = {
            "accept": "application/json",
            "x-api-key":  Get("DIDIT_API_KEY"),
            "content-type": "application/json"
        }
        payload = {
            "workflow_id": Get("DIDIT_WORKFLOW_ID"),
            "vendor_data": data.get("tracking_no"),
            "callback": Get("DIDIT_CALLBACK_URL").replace("_data_",data.get("access_token"))
        }

        result = await ApiCall(
            method="POST",
            url=url,
            headers=headers,
            payload=payload
        )
        async with AsyncSessionLocalClickKyc() as async_session:
            await _DiditSessionInsertorUpdate(result, async_session)
            await async_session.commit()
            
        diditUrl = result.get("url")
        if diditUrl:
            status.Status = "OK"
            status.Message = "Didit Session Created"
            status.Result = diditUrl
        
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "DigitServices/CreateDiditSession",
            CreatedBy = ""
        ))
        status.Status = "FAILED"
        status.Message = await GetErrorMessage(ex)
        status.Result = None
    return status

async def DiditProcessWebhookData(webhook_data: Dict[str, Any]):
    async with AsyncSessionLocalClickKyc() as async_session:
        try:
            # Process session data
            session_data = {
                "session_id": webhook_data.get("session_id"),
                "vendor_data": webhook_data.get("vendor_data"),
                "status": webhook_data.get("status", "Not Started")
            }
            await _DiditSessionInsertorUpdate(session_data, async_session)

            # Process decision data if exists
            if "decision" in webhook_data:
                decision_data = webhook_data["decision"]
                await _DiditDecisionInsertorUpdate(decision_data, async_session)

                # Process face match data if exists
                if "face_match" in decision_data:
                    await _DiditFaceMatchInsertorUpdate(decision_data["face_match"], decision_data.get("session_id"), async_session)
                    await FetchAndSaveImage(decision_data["face_match"].get("target_image"), webhook_data.get("vendor_data"), "live_photo")

                # Process ID verification data if exists
                if "id_verification" in decision_data:
                    await _DiditIdVerificationInsertorUpdate(decision_data["id_verification"], decision_data.get("session_id"), async_session)
                    await FetchAndSaveImage(decision_data["id_verification"].get("front_image"), webhook_data.get("vendor_data"), "id_front_photo")

                # Process IP analysis data if exists
                if "ip_analysis" in decision_data:
                    await _DiditIpAnalysisInsertorUpdate(decision_data["ip_analysis"], decision_data.get("session_id"), async_session)

                # Process liveness data if exists
                if "liveness" in decision_data:
                    await _DiditLivenessInsertorUpdate(decision_data["liveness"], decision_data.get("session_id"), async_session)
                
                diditSessionId = webhook_data.get("session_id")
                await AddLogOrError(SystemLogErrorSchema(
                    Msg="Process Didit Webhook Data Successfully - "+ diditSessionId,
                    Type = "LOG",
                    ModuleName = "DigitServices/DiditProcessWebhookData",
                    CreatedBy = ""
                ))
        except Exception as ex:
            await async_session.rollback()
            error_msg = f"{str(ex)}\n{traceback.format_exc()}"
            await AddLogOrError(SystemLogErrorSchema(
                Msg=error_msg,
                Type = "ERROR",
                ModuleName = "DigitServices/DiditProcessWebhookData",
                CreatedBy = ""
            ))
        finally:
            await async_session.commit()

async def _CheckForExistingData(table, session_id: str, session: AsyncSession) -> bool:
    result = await session.execute(select(table).where(table.c.session_id == session_id))
    return result.scalar() is not None

async def _DiditSessionInsertorUpdate(session_data: Dict[str, Any], async_session: AsyncSession = None):
    update_data = {
        "session_id": session_data.get("session_id"),
        "vendor_data": session_data.get("vendor_data"),
        "status": session_data.get("status", "Not Started")
    }
    session_schema = DiditSessionsSchema(**update_data)
    
    if await _CheckForExistingData(diditSessions, session_data["session_id"], async_session):
        await GenericUpdater.update_record(
            table=diditSessions,
            schema_model=DiditSessionsSchema,
            record_id=session_data["session_id"],
            update_data=session_schema,
            id_column="session_id",
            async_session=async_session,
            exclude_fields={
                "session_number", "session_token", "url", 
                "metadata", "callback", "workflow_id",
                "created_at", "updated_at"
            }
        )
    else:
        full_session_data = {
            "session_id": session_data.get("session_id"),
            "session_number": session_data.get("session_number"),
            "session_token": session_data.get("session_token"),
            "url": session_data.get("url"),
            "vendor_data": session_data.get("vendor_data"),
            "metadata": session_data.get("metadata"),
            "status": session_data.get("status", "Not Started"),
            "callback": session_data.get("callback"),
            "workflow_id": session_data.get("workflow_id")
        }
        full_session_schema = DiditSessionsSchema(**full_session_data)
        await GenericInserter.insert_record(
            table=diditSessions,
            schema_model=DiditSessionsSchema,
            data=full_session_schema,
            async_session=async_session
        )
        
async def _DiditDecisionInsertorUpdate(decision_data: Dict[str, Any], async_session: AsyncSession = None):
    decision_schema = DiditDecisionsSchema(
        session_id=decision_data.get("session_id"),
        aml=decision_data.get("aml"),
        callback=decision_data.get("callback"),
        contact_details=decision_data.get("contact_details"),
        created_at=datetime.fromisoformat(decision_data["created_at"].replace("Z", "+00:00")) if decision_data.get("created_at") else None,
        database_validation=decision_data.get("database_validation"),
        expected_details=decision_data.get("expected_details"),
        metadata=decision_data.get("metadata"),
        nfc=decision_data.get("nfc"),
        phone=decision_data.get("phone"),
        poa=decision_data.get("poa"),
        reviews = {} if isinstance(decision_data.get("reviews"), list) else decision_data.get("reviews", {}),
        status=decision_data.get("status"),
        vendor_data=decision_data.get("vendor_data"),
        workflow_id=decision_data.get("workflow_id"),
        session_url=decision_data.get("session_url"),
        session_number=decision_data.get("session_number")
    )
    if await _CheckForExistingData(diditDecisions, decision_data["session_id"], async_session):
        await GenericUpdater.update_record(
            table=diditDecisions,
            schema_model=DiditDecisionsSchema,
            record_id=decision_data["session_id"],
            update_data=decision_schema,
            id_column="session_id",
            async_session=async_session
        )
    else:
        await GenericInserter.insert_record(
            table=diditDecisions,
            schema_model=DiditDecisionsSchema,
            data=decision_schema,
            async_session=async_session
        )

async def _DiditFaceMatchInsertorUpdate(face_match_data: Dict[str, Any], session_id: str, async_session: AsyncSession = None):
    stmt = select(diditFaceMatches).where(diditFaceMatches.c.session_id == session_id)
    result = await async_session.execute(stmt)
    existing_record = result.mappings().first()

    face_match_schema = DiditFaceMatchesSchema(
        session_id=session_id,
        score=face_match_data.get("score"),
        source_image=face_match_data.get("source_image"),
        source_image_session_id=face_match_data.get("source_image_session_id"),
        status=face_match_data.get("status"),
        target_image=face_match_data.get("target_image"),
        warnings = {} if isinstance(face_match_data.get("warnings"), list) else face_match_data.get("warnings", {})
    )

    if existing_record:
        await GenericUpdater.update_record(
            table=diditFaceMatches,
            schema_model=DiditFaceMatchesSchema,
            record_id=existing_record["id"],
            update_data=face_match_schema,
            id_column="id",
            async_session=async_session
        )
    else:
        await GenericInserter.insert_record(
            table=diditFaceMatches,
            schema_model=DiditFaceMatchesSchema,
            data=face_match_schema,
            async_session=async_session
        )
    
    for warning in face_match_data.get("warnings", []):
        await _DiditWarningInsertorUpdate(async_session, session_id, warning)

async def _DiditIdVerificationInsertorUpdate(id_verification_data: Dict[str, Any], session_id: str, async_session: AsyncSession = None):
    id_verification_schema = DiditIdVerificationsSchema(
        session_id=session_id,
        address=id_verification_data.get("address"),
        age=id_verification_data.get("age"),
        back_image=id_verification_data.get("back_image"),
        back_video=id_verification_data.get("back_video"),
        date_of_birth=datetime.strptime(id_verification_data["date_of_birth"], "%Y-%m-%d") if id_verification_data.get("date_of_birth") else None,
        date_of_issue=datetime.strptime(id_verification_data["date_of_issue"], "%Y-%m-%d") if id_verification_data.get("date_of_issue") else None,
        document_number=id_verification_data.get("document_number"),
        document_type=id_verification_data.get("document_type"),
        expiration_date=datetime.strptime(id_verification_data["expiration_date"], "%Y-%m-%d") if id_verification_data.get("expiration_date") else None,
        extra_fields=id_verification_data.get("extra_fields", {}),
        extra_files={} if isinstance(id_verification_data.get("extra_files"), list) else id_verification_data.get("extra_files", {}),
        first_name=id_verification_data.get("first_name"),
        formatted_address=id_verification_data.get("formatted_address"),
        front_image=id_verification_data.get("front_image"),
        front_video=id_verification_data.get("front_video"),
        full_back_image=id_verification_data.get("full_back_image"),
        full_front_image=id_verification_data.get("full_front_image"),
        full_name=id_verification_data.get("full_name"),
        gender=id_verification_data.get("gender"),
        issuing_state=id_verification_data.get("issuing_state"),
        issuing_state_name=id_verification_data.get("issuing_state_name"),
        last_name=id_verification_data.get("last_name"),
        marital_status=id_verification_data.get("marital_status"),
        nationality=id_verification_data.get("nationality"),
        parsed_address=id_verification_data.get("parsed_address"),
        personal_number=id_verification_data.get("personal_number"),
        place_of_birth=id_verification_data.get("place_of_birth"),
        portrait_image=id_verification_data.get("portrait_image"),
        status=id_verification_data.get("status"),
        warnings = {} if isinstance(id_verification_data.get("warnings"), list) else id_verification_data.get("warnings", {})
    )

    if await _CheckForExistingData(diditIdVerifications, session_id, async_session):
        await GenericUpdater.update_record(
            table=diditIdVerifications,
            schema_model=DiditIdVerificationsSchema,
            record_id=session_id,
            update_data=id_verification_schema,
            id_column="session_id",
            async_session=async_session
        )
    else:
        await GenericInserter.insert_record(
            table=diditIdVerifications,
            schema_model=DiditIdVerificationsSchema,
            data=id_verification_schema,
            async_session=async_session
        )

    for warning in id_verification_data.get("warnings", []):
        await _DiditWarningInsertorUpdate(async_session, session_id, warning)

async def _DiditIpAnalysisInsertorUpdate(ip_analysis_data: Dict[str, Any], session_id: str, async_session: AsyncSession = None):
    ip_analysis_schema = DiditIpAnalysesSchema(
        session_id=session_id,
        browser_family=ip_analysis_data.get("browser_family"),
        device_brand=ip_analysis_data.get("device_brand"),
        device_model=ip_analysis_data.get("device_model"),
        ip_address=ip_analysis_data.get("ip_address"),
        ip_city=ip_analysis_data.get("ip_city"),
        ip_country=ip_analysis_data.get("ip_country"),
        ip_country_code=ip_analysis_data.get("ip_country_code"),
        ip_state=ip_analysis_data.get("ip_state"),
        is_data_center=ip_analysis_data.get("is_data_center", False),
        is_vpn_or_tor=ip_analysis_data.get("is_vpn_or_tor", False),
        isp=ip_analysis_data.get("isp"),
        latitude=ip_analysis_data.get("latitude"),
        longitude=ip_analysis_data.get("longitude"),
        organization=ip_analysis_data.get("organization"),
        os_family=ip_analysis_data.get("os_family"),
        platform=ip_analysis_data.get("platform"),
        status=ip_analysis_data.get("status"),
        time_zone=ip_analysis_data.get("time_zone"),
        time_zone_offset=ip_analysis_data.get("time_zone_offset"),
        warnings = {} if isinstance(ip_analysis_data.get("warnings"), list) else ip_analysis_data.get("warnings", {}),
        locations_info=ip_analysis_data.get("locations_info", {})
    )

    if await _CheckForExistingData(diditIpAnalyses, session_id, async_session):
        await GenericUpdater.update_record(
            table=diditIpAnalyses,
            schema_model=DiditIpAnalysesSchema,
            record_id=session_id,
            update_data=ip_analysis_schema,
            id_column="session_id",
            async_session=async_session
        )
    else:
        await GenericInserter.insert_record(
            table=diditIpAnalyses,
            schema_model=DiditIpAnalysesSchema,
            data=ip_analysis_schema,
            async_session=async_session
        )
        
    for warning in ip_analysis_data.get("warnings", []):
        await _DiditWarningInsertorUpdate(async_session, session_id, warning)

async def _DiditLivenessInsertorUpdate(liveness_data: Dict[str, Any], session_id: str, async_session: AsyncSession = None):
    liveness_schema = DiditLivenessSchema(
        session_id=session_id,
        age_estimation=liveness_data.get("age_estimation"),
        method=liveness_data.get("method"),
        reference_image=liveness_data.get("reference_image"),
        score=liveness_data.get("score"),
        status=liveness_data.get("status"),
        video_url=liveness_data.get("video_url"),
        warnings = {} if isinstance(liveness_data.get("warnings"), list) else liveness_data.get("warnings", {})
    )

    if await _CheckForExistingData(diditLiveness, session_id, async_session):
        await GenericUpdater.update_record(
            table=diditLiveness,
            schema_model=DiditLivenessSchema,
            record_id=session_id,
            update_data=liveness_schema,
            id_column="session_id",
            async_session=async_session
        )
    else:
        await GenericInserter.insert_record(
            table=diditLiveness,
            schema_model=DiditLivenessSchema,
            data=liveness_schema,
            async_session=async_session
        )
        
    for warning in liveness_data.get("warnings", []):
        await _DiditWarningInsertorUpdate(async_session, session_id, warning)

async def _DiditWarningInsertorUpdate(async_session,session_id: str,warning: dict):
    feature_val = warning.get("feature")
    
    stmt = select(diditWarnings).where(
        and_(
            diditWarnings.c.session_id == session_id,
            func.trim(func.upper(diditWarnings.c.feature)) == feature_val.strip().upper()
        )
    )
    result = await async_session.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing is None:
        try:
            warning_schema = DiditWarningsSchema(
                session_id=session_id,
                feature=feature_val,
                log_type=warning.get("log_type"),
                short_description=warning.get("short_description"),
                long_description=warning.get("long_description"),
                risk=warning.get("risk"),
                additional_data=warning.get("additional_data")
            )
            await GenericInserter.insert_record(
                table=diditWarnings,
                schema_model=DiditWarningsSchema,
                data=warning_schema,
                async_session=async_session
            )
        except Exception as ex:
            if "Duplicate entry" in str(ex):
                return
            else:
                raise


async def FetchDiditData(session_id: str, db_session: AsyncSession = None) -> Optional[DiditVerificationViewModelSchema]:
    try:
        # Get session data
        session_result = await db_session.execute(
            select(diditSessions).where(diditSessions.c.session_id == session_id)
        )
        session_data = session_result.mappings().first()
        
        if not session_data:
            return None
        
        current_timestamp = int(time.time())

        # Initialize the main schema
        view_data = DiditVerificationViewModelSchema(
            created_at=int(session_data['created_at'].timestamp()) if session_data['created_at'] else None,
            session_id=session_id,
            status=session_data['status'],
            vendor_data=session_data['vendor_data'],
            workflow_id=session_data['workflow_id'],
            timestamp=current_timestamp,
            decision=None
        )
        decision_model = None

        # Get decision data
        decision_result = await db_session.execute(
            select(diditDecisions).where(diditDecisions.c.session_id == session_id)
        )
        decision_data = decision_result.mappings().first()
        if decision_data:
            # Get all related data for the decision
            face_match_data = await _GetDiditFaceMatchData(session_id, db_session)
            id_verification_data = await _GetDiditIdVerificationData(session_id, db_session)
            ip_analysis_data = await _GetDiditIpAnalysisData(session_id, db_session)
            liveness_data = await _GetDiditLivenessData(session_id, db_session)
            
            # Get warnings for each feature
            warnings = await _GetDiditWarningsData(session_id, db_session)
            
            # Build decision model
            decision_model = DecisionModel(
                aml=decision_data['aml'],
                callback=decision_data['callback'],
                contact_details=decision_data['contact_details'],
                created_at=decision_data['created_at'].isoformat() if decision_data['created_at'] else None,
                database_validation=decision_data['database_validation'],
                expected_details=decision_data['expected_details'],
                face_match=face_match_data,
                features=["ID_VERIFICATION", "LIVENESS", "FACE_MATCH", "IP_ANALYSIS"],
                id_verification=id_verification_data,
                ip_analysis=ip_analysis_data,
                liveness=liveness_data,
                metadata=decision_data['metadata'],
                nfc=decision_data['nfc'],
                phone=decision_data['phone'],
                poa=decision_data['poa'],
                reviews=decision_data['reviews'] or [],
                session_id=session_id,
                session_number=decision_data['session_number'],
                session_url=decision_data['session_url'],
                status=decision_data['status'],
                vendor_data=decision_data['vendor_data'],
                workflow_id=decision_data['workflow_id']
            )
            
            # Process warnings
            
            if warnings:
                warning_models = [WarningModel(**w) for w in warnings] 
                for warning in warning_models:
                    if warning.feature.upper() in ["IDVERIFICATION", "ID_VERIFICATION"] and decision_model.id_verification:
                        decision_model.id_verification.warnings.append(warning)
                    
                    if warning.feature.upper() in ["FACEMATCH", "FACE_MATCH"] and decision_model.face_match:
                        decision_model.face_match.warnings.append(warning)
                    
                    if warning.feature.upper() in ["LIVENESS"] and decision_model.liveness:
                        decision_model.liveness.warnings.append(warning)
                    
                    if warning.feature.upper() in ["IPANALYSIS", "IP_ANALYSIS"] and decision_model.ip_analysis:
                        decision_model.ip_analysis.warnings.append(warning)
                        
        view_data.decision = decision_model

        await AddLogOrError(SystemLogErrorSchema(
            Msg="Fetch Didit Data Successfully - "+ view_data.session_id,
            Type = "LOG",
            ModuleName = "DigitServices/FetchDiditData",
            CreatedBy = ""
        ))
                
        return view_data

    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type = "ERROR",
            ModuleName = "DigitServices/CreateDiditSession",
            CreatedBy = ""
        ))
        raise ex

async def _GetDiditFaceMatchData(session_id: str, db_session: AsyncSession) -> Optional[FaceMatchModel]:
    result = await db_session.execute(
        select(diditFaceMatches).where(diditFaceMatches.c.session_id == session_id)
    )
    data = result.mappings().first()
    
    if data:
        data = dict(data)  
        if 'warnings' in data and isinstance(data['warnings'], dict):
            data['warnings'] = []
        elif 'warnings' not in data:
            data['warnings'] = [] 
        
        return FaceMatchModel(**data)

async def _GetDiditIdVerificationData(session_id: str, db_session: AsyncSession) -> Optional[IDVerificationModel]:
    result = await db_session.execute(
        select(diditIdVerifications).where(diditIdVerifications.c.session_id == session_id)
    )
    data = result.mappings().first()
    
    if data:
        data = dict(data)  
        
        date_fields = ['date_of_birth', 'date_of_issue', 'expiration_date']
        for field in date_fields:
            if field in data and isinstance(data[field], datetime):
                data[field] = data[field].isoformat()
            elif field in data and data[field] is None:
                data[field] = None
        
        if 'extra_files' in data and isinstance(data['extra_files'], dict):
                data['extra_files'] = []
        elif data['extra_files'] is None:
            data['extra_files'] = []
                
        if 'warnings' in data and isinstance(data['warnings'], dict):
            data['warnings'] = []
        elif 'warnings' not in data:
            data['warnings'] = [] 
        
    return IDVerificationModel(**data)

async def _GetDiditIpAnalysisData(session_id: str, db_session: AsyncSession) -> Optional[IPAnalysisModel]:
    result = await db_session.execute(
        select(diditIpAnalyses).where(diditIpAnalyses.c.session_id == session_id)
    )
    data = result.mappings().first()
    
    if data:
        data = dict(data)  
        if 'warnings' in data and isinstance(data['warnings'], dict):
            data['warnings'] = []
        elif 'warnings' not in data:
            data['warnings'] = [] 
        
        locations_info = data.get('locations_info')
        if locations_info:
            data['locations_info'] = LocationsInfoModel(**locations_info)
        return IPAnalysisModel(**data)
    return None

async def _GetDiditLivenessData(session_id: str, db_session: AsyncSession) -> Optional[LivenessModel]:
    result = await db_session.execute(
        select(diditLiveness).where(diditLiveness.c.session_id == session_id)
    )
    data = result.mappings().first()
    
    if data:
        data = dict(data)  
        if 'warnings' in data and isinstance(data['warnings'], dict):
            data['warnings'] = []
        elif 'warnings' not in data:
            data['warnings'] = [] 
        
    return LivenessModel(**data) 

async def _GetDiditWarningsData(session_id: str, db_session: AsyncSession) -> List[Dict]:
    result = await db_session.execute(
        select(diditWarnings).where(diditWarnings.c.session_id == session_id)
    )
    return [dict(row) for row in result.mappings().all()]

async def FetchAndSaveImage(image_url:str, tracking_no:str, image_name:str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                image_url,
                headers={"Accept": "image/*"},
                timeout=30
            )
        
        image_bytes = response.content
                
        if b"AccessDenied" in image_bytes:
            raise ValueError("Access denied. Image not available now.")
        
        image = Image.open(BytesIO(image_bytes))
        with BytesIO() as buffer:
            image.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
        encrypted_image = await EncryptImage(image_bytes)
        encrypted_tracking_no = await GetSha1Hash(tracking_no)
        save_dir = os.path.join('/app/CustomerPhotos', encrypted_tracking_no)
        os.makedirs(save_dir, exist_ok=True)

        filename = f"{image_name}.bin"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(encrypted_image)
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="DigitServices/FetchAndSaveImage",
            CreatedBy=""
        ))