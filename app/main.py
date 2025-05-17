from fastapi import FastAPI
from app.sentry_setup import setup_sentry
from app.dependencies import get_db
from app.auth import auth_router
from app.telegram import telegram_router
from app.autopost import autopost_router, scheduler

app = FastAPI(title="Масштабируемый бот")

setup_sentry()

app.include_router(auth_router, prefix="/auth")
app.include_router(telegram_router, prefix="/telegram")
app.include_router(autopost_router, prefix="/autopost")

@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
