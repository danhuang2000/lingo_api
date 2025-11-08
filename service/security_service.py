from pydantic import BaseModel


class SecurityService:
    class UserCredentials(BaseModel):
        user_uuid: str
        mfa_code: str


    def __init__(self, session):
        self.session = session


    def validate_user_credentials(self, credentials: UserCredentials) -> bool:
        # validate the user
        return False