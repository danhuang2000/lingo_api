from entity import User
from datetime import datetime, timezone

class UserOrm:
    def add_user(self, session, user):
        user.create_date = user.update_date = datetime.now(timezone.utc)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    

    def get_user(self, session, user_id):
        return session.query(User).filter_by(id=user_id).first()
    
    
    def update_user(self, session, user):
        old_user = session.query(User).filter_by(id=user.id).first()
        if old_user:
            old_user.name = user.name
            old_user.email = user.email
            old_user.phone = user.phone
            old_user.update_date = datetime.now(timezone.utc)
            session.commit()
            session.refresh(old_user)
            return old_user
        return None

