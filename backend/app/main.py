from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import complaints, chat

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AIVOA Complaint Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to settings.CORS_ORIGINS in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
