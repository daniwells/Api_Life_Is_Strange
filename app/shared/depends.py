from app.db.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_user import UserUseCases
from sqlalchemy.orm import Session
from fastapi import Depends

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def get_db_session():
    try: 
        session = SessionLocal()
        yield session
    finally:
        session.close()


def token_verifier(
    db_session: Session = Depends(get_db_session),
    token = Depends(oauth_scheme),
):
    uc = UserUseCases(db_session=db_session)
    uc.verify_token(token=token)