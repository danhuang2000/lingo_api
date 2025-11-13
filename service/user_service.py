import uuid
import logging

from sqlmodel import Session, select
from entity import User
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, session: Session):
        self.session = session

        
    def add_user(self, user):
        user.create_date = user.update_date = datetime.now(timezone.utc)
        user.uuid = str(uuid.uuid4())
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        logger.info(f"Added new user: {user.uuid}")
        return user
    

    def get_user_by_uuid(self, uuid: str):
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


