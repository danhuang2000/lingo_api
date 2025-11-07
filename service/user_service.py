import uuid
import logging

from sqlmodel import Session, select
from entity import User, UserLevel, UserLevelHistory
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


    def get_level_by_user(self, user, language):
        statement = (select(UserLevel)
                .join(User, UserLevel.user_id == User.id)
                .where((User.id == user.id) & (User.language_id == language.id))
            )
        result = self.session.exec(statement).first()
        return result
        

    def set_user_level(self, user, language, level):
        user_level = UserLevel(user_id=user.id, language_id=language.id, level=level)
        user_level.update_date = datetime.now(timezone.utc)
        self.session.add(user_level)

        history = UserLevelHistory(
            user_id=user.id,
            language_id=language.id,
            level=level,
            create_date=datetime.now(timezone.utc)
        )
        self.session.add(history)

        self.session.commit()
        return user_level

    
    def add_user_level_history(self, user_id, language_id, level):
        history = UserLevelHistory(
            user_id=user_id,
            language_id=language_id,
            level=level,
            create_date=datetime.now(timezone.utc)
        )
        self.session.add(history)
        self.session.commit()
        return history
    

    def get_user_level_history(self, user_id, language_id):
        return self.session.query(UserLevelHistory).filter_by(
            user_id=user_id,
            language_id=language_id
        ).all()

    
    def delete_user_level_history(self, user_id):
        histories = self.session.query(UserLevelHistory).filter_by(
            user_id=user_id
        ).delete()
        self.session.commit()
