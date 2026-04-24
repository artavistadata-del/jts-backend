from fastapi import FastAPI
from config.config import engine
from departments import department_route
from finance import finance_router
from history import history_router
from models.models import models 
from users import user_route
from roles import role_route
# from cleaning import route_finance
from fastapi.middleware.cors import CORSMiddleware

from upload import minio_route

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Manajemen User",
    description="Sistem registrasi dan login",
    version="1.0.0"
)

origins = [
    "*"
    "http://localhost:5173",     
    "https://jts.adhibagus.com",  
]
app.add_middleware(
    CORSMiddleware,
    # allow_origins=['*'],
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(user_route.router)
app.include_router(minio_route.router)
app.include_router(role_route.router)
app.include_router(department_route.router)
app.include_router(finance_router.router)
app.include_router(history_router.router)
# app.include_router(route_finance.router)

@app.get("/")
def health_check():
    return {"status": "Server berjalan normal!"}