from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from config.dependencies import get_history_service
from core.security import get_current_user
from history.history_service import HistoryService
from models.models.models import Users
# Import database session, models, dan schemas kamu di sini

router = APIRouter(
        prefix="/history",
        tags=["History"]
    )


@router.get("/all-transaction")
def read_history(
    userNow : Users = Depends(get_current_user), 
    page: int = Query(1, ge=1), # Default page 1, minimal 1
    limit: int = Query(10, ge=1, le=100), # Default 10, max 100 per page
    service : HistoryService = Depends(get_history_service)
):

    result = service.get_history_paginated(userNow.nik, page, limit)
    return result