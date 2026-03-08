from fastapi import APIRouter, UploadFile, File, HTTPException
from pdf2image import convert_from_bytes
from typing import cast
import pytesseract

router = APIRouter()


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)) -> dict[str, str | int | list[str] | None]:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")

    contents = await file.read()

    try:
        images = convert_from_bytes(contents)  # type: ignore[reportUnknownMemberType]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to process PDF: {e}")

    pages: list[str] = []
    for image in images:
        text = pytesseract.image_to_string(image, lang="ces+eng")
        pages.append(text)

    return {"filename": file.filename, "size": len(contents), "pages": pages}
