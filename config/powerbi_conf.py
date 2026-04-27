from fastapi import APIRouter, Depends, HTTPException
import httpx
import os
from dotenv import load_dotenv
from config.dept_registry import get_powerbi_config
from core.security import get_current_user
from models.models.models import Users

load_dotenv()

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")