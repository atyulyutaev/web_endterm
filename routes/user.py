from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status
from typing_extensions import Annotated

from adapters.database import get_db
from adapters.token_helpers import auth_scheme, SECRET_KEY, ALGORITHM, pwd_context, verify_password, create_access_token
from repositories.user import get_user_by_email, create_user
from schemas.token import TokenData, Token
from schemas.user import User, UserCreate

from fastapi import APIRouter

router = APIRouter()


async def validate_credentials(token: Annotated[str, Depends(auth_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials provided",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def validate_active_user(
        authenticated_user: Annotated[User, Depends(validate_credentials)]
):
    if not authenticated_user.is_active:
        raise HTTPException(status_code=400, detail="User account is inactive")
    return authenticated_user


@router.post("/signup/", response_model=User)
def user_signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")
    user.password = pwd_context.hash(user.password)
    return create_user(db=db, user=user)


@router.post("/login/", response_model=Token)
def user_login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me/", response_model=User)
async def get_user_profile(
        active_user: Annotated[User, Depends(validate_active_user)]
):
    return active_user
