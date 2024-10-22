from sqlalchemy.orm import Session
from app.db.models.user_model import UserModel
from app.db.models.refresh_token_model import RefreshTokenModel
from app.schemas.user_schemas import UserSchema
from passlib.context import CryptContext
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from fastapi import status
from datetime import datetime, timedelta
from jose import jwt, JWTError
from decouple import config

SECRET_KEY = config("SECRET_KEY")
REFRESH_SECRET_KEY = config("REFRESH_SECRET_KEY")
ALGORITHM = config("ALGORITHM")
crypt_context = CryptContext(schemes=["sha256_crypt"])

class UserUseCases:
    def __init__(self, db_session: Session):
        self.db_session = db_session


    def user_register(self, user: UserSchema):
        user_model = UserModel(
            username=user.username,
            password=crypt_context.hash(user.password)
        )
        try:
            self.db_session.add(user_model)
            self.db_session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists!"
            )
        

    def user_login(self, user: UserSchema, expires_in: int = 30, refresh_expires_in: int = 1440):
        user_on_db = self.db_session.query(UserModel).filter_by(username=user.username).first()

        if user_on_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password!"
            )

        if not crypt_context.verify(user.password, user_on_db.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password!"
            )

        # Generating access token
        access_expiration_date = datetime.utcnow() + timedelta(minutes=expires_in)
        access_payload = {
            "sub": user.username,
            "exp": access_expiration_date
        }
        access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

        # Generating refresh token
        refresh_expiration_date = datetime.utcnow() + timedelta(minutes=refresh_expires_in)
        refresh_payload = {
            "sub": user.username,
            "exp": refresh_expiration_date
        }
        refresh_token = jwt.encode(refresh_payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
        
        # Salvar refresh token no banco de dados
        token_exist = self.db_session.query(RefreshTokenModel).filter_by(token=refresh_token).first()
        
        if token_exist is None:
            refresh_token_model = RefreshTokenModel(
                user_id=user_on_db.id,
                token=refresh_token,
                expiration_date=refresh_expiration_date
            )
            self.db_session.add(refresh_token_model)
            self.db_session.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_token_exp": access_expiration_date.isoformat(),
            "refresh_token_exp": refresh_expiration_date.isoformat()
        }
    

    def verify_token(self, token, token_type="access"):
        try:
            if token_type == "refresh":
                data = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
                
                token_entry = self.db_session.query(RefreshTokenModel).filter_by(token=token).first()
                if token_entry is None or token_entry.revoked or token_entry.expiration_date < datetime.utcnow():
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, 
                        detail="Invalid or revoked refresh token!"
                    )
            else:
                data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token!"
            )

        user_on_db = self.db_session.query(UserModel).filter_by(username=data["sub"]).first()
        
        if user_on_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid access token!"
            )

        return user_on_db
    
    
    def refresh_access_token(self, refresh_token: str, access_expires_in: int = 30):
        user_data = self.verify_token(refresh_token, token_type="refresh")
        
        access_expiration_date = datetime.utcnow() + timedelta(minutes=access_expires_in)
        access_payload = {
            "sub": user_data.username,
            "exp": access_expiration_date
        }

        new_access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": new_access_token,
            "access_token_exp": access_expiration_date.isoformat()
        }

    
    def revoke_refresh_token(self, refresh_token: str):
        token_entry = self.db_session.query(RefreshTokenModel).filter_by(token=refresh_token).first()
        if token_entry:
            token_entry.revoked = True
            self.db_session.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Token not found!"
            )