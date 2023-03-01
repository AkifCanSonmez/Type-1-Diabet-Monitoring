from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
import uvicorn
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from routers import auth, newmeal, crud

app = FastAPI()

templates = Jinja2Templates(directory="templates")


app.add_middleware(SessionMiddleware, secret_key="secret_key")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(newmeal.router)
app.include_router(crud.router)



