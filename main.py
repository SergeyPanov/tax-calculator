from fastapi import FastAPI

from routers.pdf import router as pdf_router

app = FastAPI()
app.include_router(pdf_router)