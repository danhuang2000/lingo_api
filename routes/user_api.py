import logging
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from db.database import get_session

from entity import User
from service import UserService, SecurityService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/device/challenge")
def get_device_challenge(user: User, session=Depends(get_session)):
    service = UserService(session=session)
    challenge = service.generate_device_challenge(user)
    logger.debug(f"Challenge: {challenge.challenge} {challenge.device_uuid}")
    return challenge

@router.post("/device/cert")
def attest_device(request: SecurityService.AttestationRequest, session=Depends(get_session)):
    service = SecurityService(session=session)
    challenge = service.attest_request(request)
    if not challenge:
        raise HTTPException(status_code=400, detail="Item ID must be a positive integer.")
    
    return challenge


@router.post("/device/verify")
def assert_device(request: SecurityService.AssertionRequest, session=Depends(get_session)):
    service = SecurityService(session=session)
    valid, device_uuid, user_uuid = service.assert_request(request)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid device.")
    return {"device_uuid": device_uuid, "user_uuid": user_uuid}

@router.post("/add")
def add_user(user: User, session=Depends(get_session)):
    # TODO validate token
    user_service = UserService(session=session)
    return user_service.add_user(user)


@router.get("/get/{user_uuid}")
def get_user(user_uuid: str, session=Depends(get_session)):
    # TODO validate token
    user_service = UserService(session=session)
    user = user_service.get_user_by_uuid(user_uuid)
    return user


@router.post("/login")
def post_session_token(credentials: SecurityService.UserCredentials, session=Depends(get_session)):
    service = SecurityService(session=session)
    result = service.validate_user_credentials(credentials)
    return result

@router.get("/token/new")
def create_session_token(session=Depends(get_session)):
    service = SecurityService(session=session)
    token = service.create_new_user_token()
    return {"token": token}

@router.post("/token/attest")
def get_session_token(request: SecurityService.AttestationRequest, session=Depends(get_session)):
    service = SecurityService(session=session)
    valid, uuid = service.assert_request(request)
    return {"is_valid": valid}


@router.post("/token/assert")
def attest_session_token(request: SecurityService.AttestationRequest, session=Depends(get_session)):
    service = SecurityService(session=session)
    valid, user_uuid = service.attest_request(request)
    return {"is_valid": valid}