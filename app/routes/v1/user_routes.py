from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.shared.depends import get_db_session, token_verifier
from app.services.auth_user import UserUseCases
from app.schemas.user_schemas import UserSchema 
from fastapi.security import OAuth2PasswordRequestForm
from app.db.models.user_model import UserModel

user_router = APIRouter(prefix="/user")
test_router = APIRouter(prefix="/test", dependencies=[Depends(token_verifier)])

@user_router.post("/register")
def post_user(
    user: UserSchema,
    db_session: Session = Depends(get_db_session)

):
    uc = UserUseCases(db_session=db_session)
    uc.user_register(user=user)
    return JSONResponse(
        content={"msg": "success"},
        status_code=status.HTTP_201_CREATED
    )

@user_router.post("/login")
def login_user(
    request_form_user: OAuth2PasswordRequestForm = Depends(),
    db_session: Session = Depends(get_db_session)
):
    uc = UserUseCases(db_session=db_session)

    user = UserModel(
        username=request_form_user.username,
        password=request_form_user.password 
    )

    uc.user_login(user=user)

    auth_data = uc.user_login(user=user)
    return JSONResponse(
        content = auth_data,
        status_code=status.HTTP_200_OK
    )


@test_router.get("/test")
def test_user_verify():
    return "It works"


@user_router.post("/token/refresh")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db_session)):
    uc = UserUseCases(db_session=db)
    new_tokens = uc.refresh_access_token(refresh_token)
    return new_tokens


@user_router.post("/logout")
async def logout(refresh_token: str, username=Depends(token_verifier), db: Session = Depends(get_db_session)):
    uc = UserUseCases(db_session=db)
    uc.revoke_refresh_token(refresh_token)
    return JSONResponse(
        content = "Logout successful",
        status_code=status.HTTP_200_OK
    )