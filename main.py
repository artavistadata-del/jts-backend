from fastapi import FastAPI
from config.config import engine
from models import models 
from routes import user_route, minio_route
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Manajemen User",
    description="Sistem registrasi dan login",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_route.router)
app.include_router(minio_route.router)

@app.get("/")
def health_check():
    return {"status": "Server berjalan normal!"}