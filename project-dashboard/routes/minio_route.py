from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from services.minio_service import MinioService
from config.dependencies import get_minio_service 

router = APIRouter(
    prefix='/file',
    tags=["File"]
)

@router.post("/upload-gaji")
async def upload_payroll_excel(
    minio_service: MinioService = Depends(get_minio_service),
    file: UploadFile = File(...)
):
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(
            status_code=400, 
            detail="Format ditolak. Harap unggah file Excel (.xls atau .xlsx)"
        )

    try:
        file_content = await file.read()
    except Exception:
        raise HTTPException(status_code=500, detail="Gagal membaca file dari request")

    result = minio_service.upload_file( 
        file_name=file.filename,
        content=file_content,
        content_type=file.content_type
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
        
    return {
        "message": "File Excel berhasil diunggah ke gudang data!",
        "detail": result
    }