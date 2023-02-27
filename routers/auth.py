import sys
sys.path.append("..")

from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from database import SessionLocal, engine
from datetime import datetime, timedelta
import models

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)


SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7" # change this to a secure value
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def authenticate_user(username, password, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()
    if user:
        if password != user.password:
            return None
        user_id = user.user_id
        return user_id
    else:
        return None
    

async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        if user_id is None:
            raise JWTError
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_id


def create_access_token(username: str, user_id: int):

    # Authentication successful, generate JWT token
    access_token_expires_in_minutes = 30
    expires_at = datetime.utcnow() + timedelta(minutes=access_token_expires_in_minutes)
    access_token = jwt.encode({"id": user_id, "exp": expires_at}, SECRET_KEY, algorithm=ALGORITHM)
    return access_token


@router.get("/")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/home/")
async def home(request:Request, username: str = Form(...), password: str = Form(...),
               db: Session = Depends(get_db)):

    user = await authenticate_user(username, password, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(username, password)
    response = templates.TemplateResponse("home.html", {"request": request})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    
    return response