from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from config.dependencies import get_history_service
from core.security import get_current_user
from history.history_service import HistoryService
from models.models.models import Users
# Import database session, models, dan schemas kamu di sini

router = APIRouter(
        prefix="/v1/history",
        tags=["History"]
    )


@router.get("/all")
def read_history(
    userNow: Users = Depends(get_current_user), 
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100), 
    service: HistoryService = Depends(get_history_service)
):

    result = service.get_history_paginated(userNow, page, limit)
    return result