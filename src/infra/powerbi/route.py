from fastapi import APIRouter, Depends, HTTPException
import httpx
from src.modules.departments.registry import get_powerbi_config
from src.infra.powerbi.client import TENANT_ID, CLIENT_ID, CLIENT_SECRET
from src.core.security import get_current_user
from src.models.models import RoleEnum, Users

router = APIRouter(prefix="/v1/reports", tags=["Power BI"])

async def get_aad_token():
    """Meminta Access Token dari Microsoft Entra ID (Azure)"""
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://analysis.windows.net/powerbi/api/.default",
        "grant_type": "client_credentials"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        
        if response.status_code != 200:
            print("Azure Error:", response.text) 
            raise HTTPException(status_code=500, detail="Gagal mendapatkan token dari Azure")
            
        return response.json().get("access_token")
    
@router.post("/generate-token")
async def get_powerbi_token(current_user: Users = Depends(get_current_user)):
    
    try:
        pbi_config = get_powerbi_config(current_user.department_id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    # 2. Siapkan data untuk tembak Microsoft
    aad_token = await get_aad_token()
    pbi_api_url = "https://api.powerbi.com/v1.0/myorg/GenerateToken"
    
    headers = {
        "Authorization": f"Bearer {aad_token}",
        "Content-Type": "application/json"
    }
    
    # Gunakan ID dari registry
    body = {
        "reports": [ { "id": pbi_config["report_id"] } ],
        "datasets": [ { "id": pbi_config["dataset_id"] } ],
        "accessLevel": "View"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(pbi_api_url, headers=headers, json=body)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Gagal meminta token dari Power BI")
            
        # 3. Opsional: Tambahkan embedUrl ke response JSON jika mau
        # Ini sangat membantu Frontend!
        result = response.json()
        report_id = pbi_config["report_id"],
        dataset_id= pbi_config["dataset_id"]
        result["reportId"] = pbi_config["report_id"]
        
        return result
        # return report_id, dataset_id


@router.post("/generate-token/finance")
async def get_powerbi_token(current_user: Users = Depends(get_current_user)):
    
    if current_user.role.name != RoleEnum.ADMIN.value :
        raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke endpoint ini")

    try:
        pbi_config = get_powerbi_config(1)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    # 2. Siapkan data untuk tembak Microsoft
    aad_token = await get_aad_token()
    pbi_api_url = "https://api.powerbi.com/v1.0/myorg/GenerateToken"
    
    headers = {
        "Authorization": f"Bearer {aad_token}",
        "Content-Type": "application/json"
    }
    
    # Gunakan ID dari registry
    body = {
        "reports": [ { "id": pbi_config["report_id"] } ],
        "datasets": [ { "id": pbi_config["dataset_id"] } ],
        "accessLevel": "View"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(pbi_api_url, headers=headers, json=body)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Gagal meminta token dari Power BI")
            
        # 3. Opsional: Tambahkan embedUrl ke response JSON jika mau
        # Ini sangat membantu Frontend!
        result = response.json()
        report_id = pbi_config["report_id"],
        dataset_id= pbi_config["dataset_id"]
        result["reportId"] = pbi_config["report_id"]
        
        return result


@router.post("/generate-token/purchasing")
async def get_powerbi_token(current_user: Users = Depends(get_current_user)):
    
    if current_user.role.name != RoleEnum.ADMIN.value :
        raise HTTPException(status_code=403, detail="Anda tidak memiliki akses ke endpoint ini")

    try:
        pbi_config = get_powerbi_config(3)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    
    # 2. Siapkan data untuk tembak Microsoft
    aad_token = await get_aad_token()
    pbi_api_url = "https://api.powerbi.com/v1.0/myorg/GenerateToken"
    
    headers = {
        "Authorization": f"Bearer {aad_token}",
        "Content-Type": "application/json"
    }
    
    # Gunakan ID dari registry
    body = {
        "reports": [ { "id": pbi_config["report_id"] } ],
        "datasets": [ { "id": pbi_config["dataset_id"] } ],
        "accessLevel": "View"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(pbi_api_url, headers=headers, json=body)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Gagal meminta token dari Power BI")
            
        # 3. Opsional: Tambahkan embedUrl ke response JSON jika mau
        # Ini sangat membantu Frontend!
        result = response.json()
        report_id = pbi_config["report_id"],
        dataset_id= pbi_config["dataset_id"]
        result["reportId"] = pbi_config["report_id"]
        
        return result