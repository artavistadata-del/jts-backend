from fastapi import APIRouter, UploadFile, File, HTTPException
from cleaning.finance import FinanceBSService

router = APIRouter(
    prefix="/finance",
    tags=["Finance"]
)

@router.post("/upload-bs")
async def upload_balance_sheet(file: UploadFile = File(...)):
    # 1. Validasi ekstensi file
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(
            status_code=400, 
            detail="Format file ditolak. Harap unggah file Excel (.xls atau .xlsx)"
        )
        
    try:
        # 2. Baca isi file ke memori (bytes)
        file_bytes = await file.read()
        
        # 3. Panggil service Polars untuk memproses data
        result_data = FinanceBSService.process_balance_sheet(file_bytes)
        
        # 4. Kembalikan response sukses
        return {
            "status": "success",
            "message": f"Berhasil memproses {len(result_data)} baris data.",
            "data": result_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses file: {str(e)}")