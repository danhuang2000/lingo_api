import os
import uuid
import time

from utils import get_app_logger
from sqlmodel import Session, select
from entity import User, Device
from datetime import datetime, timezone

logger = get_app_logger(__name__)

class UserService:
    class DeviceChallenge:
        def __init__(self, challenge: str, device_uuid: str):
            self.challenge = challenge
            self.device_uuid = device_uuid


    def __init__(self, session: Session):
        self.session = session

    def generate_device_challenge(self, user: User) -> DeviceChallenge:
        logger.info(f"Generating device challenge for user: {user.uuid}")
        
        if user.uuid:
             user = self.get_user_by_uuid(user.uuid)

        if not user.uuid:
            user = self.add_user(user)
    
        device_uuid = str(uuid.uuid4())
        challenge = os.urandom(16).hex()
        device = Device(uuid=device_uuid, user_id=user.id, challenge=challenge, create_date=datetime.now(timezone.utc))
        device.user = user
        self.session.add(device)
        self.session.commit()
        self.session.refresh(device)
        return UserService.DeviceChallenge(challenge=challenge, device_uuid=device_uuid)

    def update_device_challenge(self, device_uuid: str, new_challenge: str):
        statement = select(Device).where(Device.uuid == device_uuid)
        device = self.session.exec(statement).first()
        if device:
            device.challenge = new_challenge
            self.session.add(device)
            self.session.commit()
            self.session.refresh(device)
            return device
        return None

    def get_device(self, device_uuid: str):
        statement = select(Device).where(Device.uuid == device_uuid)
        device = self.session.exec(statement).first()
        if device:
            return device
        return None

    def set_device_key_info(self, device_uuid: str, key_id: str, key_pem: str):
        statement = select(Device).where(Device.uuid == device_uuid)
        device = self.session.exec(statement).first()
        if device:
            device.key_id = key_id
            device.public_key = key_pem
            self.session.add(device)
            self.session.commit()
            self.session.refresh(device)
            return device
        return None
        

    def add_user(self, user):
        user.create_date = user.update_date = datetime.now(timezone.utc)
        user.uuid = str(uuid.uuid4())
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        logger.info(f"Added new user: {user.uuid}")
        return user
    

    def get_user_by_uuid(self, uuid: str) -> User:
        statement = select(User).where(User.uuid == uuid)
        result = self.session.exec(statement).first()
        if result == None:
            result = User()
        return result
   
    
    def update_user(self, user):
        old_user = self.get_user(user.id)
        if old_user:
            old_user.name = user.name
            old_user.email = user.email
            old_user.phone = user.phone
            old_user.update_date = datetime.now(timezone.utc)
            self.session.commit()
            self.session.refresh(old_user)
            return old_user
        return old_user
    

    def update_user_info(self, user_uuid, name=None, email=None, phone=None):
        user = self.get_user_by_uuid(user_uuid)
        self.update_user(user)
        return user


    def delete_user(self, user_id):
        user = self.session.get(User, user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def add_device_to_user(self, user_uuid: str, device):
        user = self.get_user_by_uuid(user_uuid)
        if user:
            user.devices.append(device)
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return device
        else:
            logger.info(f"User with UUID {user_uuid} not found.")
        return None

