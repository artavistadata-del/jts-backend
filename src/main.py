from fastapi import FastAPI
from src.core.database import engine
from src.modules.departments import route as dept_router
from src.modules.history import route as history_router
from src.models import models 
from src.models import stg_table
from src.modules.transaction.finance import models
from src.modules.transaction.purchasing import models
from src.modules.transaction.sales import models


from src.infra.powerbi import route as powerbi_router
from src.modules.transaction.finance import route as finance_transaction_router
from src.modules.transaction.purchasing import route as purchasing_transaction_router
from src.modules.users import route as users_router
from src.modules.roles import route as roles_router
from fastapi.middleware.cors import CORSMiddleware

from src.infra.upload import route as upload_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Manajemen User",
    description="Sistem registrasi dan login",
    version="1.0.0"
)

origins = [
    "http://localhost:5173",
    "http://localhost:4174",
    "https://jts.artavista.net",
    "https://jts-dev.artavista.net"
]
app.add_middleware(
    CORSMiddleware,
    # allow_origins=['*'],
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(dept_router.router)
app.include_router(history_router.router)
app.include_router(powerbi_router.router)
app.include_router(finance_transaction_router.router)
app.include_router(purchasing_transaction_router.router)
app.include_router(users_router.router)
app.include_router(roles_router.router)
app.include_router(upload_router.router)

@app.get("/v1")
def health_check():
    return {"status": "Server berjalan normal!"}