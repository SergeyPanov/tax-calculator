from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)) -> dict[str, str | int | None]:
    # Validate it's a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    contents = await file.read()

    # Do something with the PDF bytes...
    return {"filename": file.filename, "size": len(contents)}