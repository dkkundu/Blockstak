from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from config.mysql_connection import Base, engine, get_db
from passlib.context import CryptContext
from datetime import datetime, timedelta
from config.settings import get_settings
from jose import JWTError, jwt
from core.models import User
from abstract.api_responces import Helper
from config.logger import logger

response = Helper()
settings = get_settings()
oauth2_router = APIRouter()

Base.metadata.create_all(bind=engine)  # ✅ Correct way
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Authentication function


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if user and pwd_context.verify(password, user.password):
        logger.info(f"User '{username}' authenticated successfully.")
        return user
    logger.error(f"Authentication failed for user '{username}'.")
    return None


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug(f"Access token created for: {data.get('sub')}")
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_MINUTES))  # 7 days default
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug(f"Refresh token created for: {data.get('sub')}")
    return encoded_jwt


async def get_current_client(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.error("JWT payload did not contain 'sub'.")
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT decode failed: {str(e)}")
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logger.error(f"User not found in DB for token sub: {username}")
        raise credentials_exception
    logger.debug(f"User '{username}' retrieved successfully from token.")
    return user


@oauth2_router.post("/register")
async def register_user(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        logger.error(f"Registration attempt failed: Username '{username}' already exists.")
        return response.error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Unable to register user. Username already exists.",
            errors=[{"username": "Username already registered"}]
        )
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, password=hashed_password, scope="api:access")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"New user registered: {username}")
    return response.success_response(
        status_code=status.HTTP_201_CREATED,
        data={"username": new_user.username},
        message="User registered successfully"
    )


@oauth2_router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        logger.error(f"Login failed for username: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=7)

    access_token = create_access_token(data={"sub": user.username, "scope": user.scope}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)

    logger.info(f"User '{user.username}' logged in successfully.")
    return response.success_response(
        status_code=status.HTTP_200_OK,
        data={
            "username": user.username,
            "scope": user.scope,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        },
        message="Login successful"
    )


@oauth2_router.post("/refresh")
async def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            logger.error("Refresh token missing subject.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except JWTError as e:
        logger.error(f"Refresh token decode error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logger.error(f"Refresh token rejected. User not found: {username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access_token = create_access_token(data={"sub": user.username, "scope": user.scope},
                                           expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    logger.info(f"Access token refreshed for user: {user.username}")
    return response.success_response(
        status_code=status.HTTP_200_OK,
        data={
            "username": user.username,
            "scope": user.scope,
            "access_token": new_access_token,
            "token_type": "bearer"
        },
        message="Refresh successful"
    )
