import crud
from tables import Account
from datetime import datetime, timedelta
from database import SessionLocal
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Form, HTTPException, Depends, status
import sys
sys.path.append("..")


templates = Jinja2Templates(directory="templates")
router = APIRouter(
    prefix="",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)

# to create access token
SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"  # change this to a secure value
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def authenticate_user(username, password, db):
    username = username.lower()
    password = password.lower()

    # Query the database for the user with the given username, and check it
    user = db.query(Account).filter(Account.username == username).first()
    if user:
        if password != user.user_password:
            return None
        return user
    else:
        return None


async def get_current_user(request: Request):
    """
    Retrieve the current user's information (username and ID) from the JWT token in cookies.

    Args:
        request (Request): FastAPI request object containing the cookies.

    Returns:
        Optional[dict]: A dictionary containing the username and user ID if the token is valid, None otherwise.
    """
    try:
        # Extract the JWT access token from the request cookies
        access_token = request.cookies.get("access_token")

        # If there's no access token, return None
        if access_token is None:
            return None

        # Decode the JWT access token using the secret key and algorithm
        token_payload = jwt.decode(
            access_token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract the username and user ID from the token payload
        username: str = token_payload.get("sub")
        user_id: int = token_payload.get("id")

        # If either the username or user ID is missing, raise a JWTError
        if username is None or user_id is None:
            return None

        # Return the user's information as a dictionary
        return {"username": username, "id": user_id}

    except jwt.JWTError:
        return None


@router.get("/")
async def root(request: Request):
    user = await get_current_user(request)

    if user is None:
        return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
    else:
        return RedirectResponse("/home", status_code=status.HTTP_302_FOUND)


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/create-access-token")
async def create_access_token_route(request: Request, username: str = Form(...), password: str = Form(...),
                                    db: Session = Depends(get_db)) -> str:
    """
    Create a JWT access token for the given user.

    Args:
        username (str): The username of the authenticated user.
        user_id (int): The ID of the authenticated user.

    Returns:
        str: The generated JWT access token.
    """
    user = await authenticate_user(username, password, db)
    if user is None:
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode(
        {"sub": username, "id": user.pk_user, "exp": expires_at}, SECRET_KEY, algorithm=ALGORITHM)

    response = RedirectResponse("/home", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return response


@router.get("/logout")
async def logout(request: Request):
    response = templates.TemplateResponse("login.html", {"request": request})
    response.delete_cookie(key="access_token")
    return response


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_user(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    username = form["username"]
    password = form["password"]
    email = form["email"]
    age = int(form["age"])
    weight = float(form["weight"])
    height = float(form["height"])
    body_fat = float(form["body-fat"])
    activity = form["activity"]

    validation1 = db.query(Account).filter(
        Account.username == username).first()
    validation2 = db.query(Account).filter(Account.email == email).first()

    if validation1 is not None or validation2 is not None:
        msg = "The username or email you entered is already in use. Please choose a different username or email. "
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

    account = Account(username=username, user_password=password, email=email, age=age,
                      weight=weight, height=height, body_fat=body_fat, activity=activity,
                      created_on=datetime.now(), last_login=datetime.now()
                      )

    db.add(account)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
