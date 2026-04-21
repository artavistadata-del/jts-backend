import requests

# Ganti dengan token JWT kamu yang valid
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyMDAzMjAwMDIwMDQyMDAwIiwiZXhwIjoxNzc2NjgyMDU1fQ.RWf3jFVHVVgcPwCl38j4pITZvig70SuoI2S2eH1co24" 

url = "http://localhost:8000/file/upload-file"
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# Pastikan path file benar. 'rb' artinya read-binary (streaming aman)
file_path = "100mb.xlsx" 

print(f"Mulai mengunggah {file_path}...")

with open(file_path, "rb") as f:
    files = {
        # Format: "nama_field_di_fastapi": ("nama_file", isi_file, "mime_type")
        "file": ("100mb.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    }
    
    response = requests.post(url, headers=headers, files=files)

print("Status Code:", response.status_code)
print("Response:", response.json())