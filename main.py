import time
import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.contacts.routes import router as contacts
from src.phones.routes import router as phones
from src.emails.routes import router as emails
from src.auth.routes import router as auth
from src.mailing.routes import router as mailing
from src.user.routes import router as user
from src.database_redis import redis_db

app = FastAPI()

origins = ["http://localhost:3000"]

app.include_router(auth, prefix='/api')
app.include_router(user, prefix='/api')
app.include_router(mailing, prefix='/api')

app.include_router(contacts, prefix='/api')
app.include_router(phones, prefix='/api')
app.include_router(emails, prefix='/api')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.on_event("startup")
async def startup():
    await FastAPILimiter.init(await redis_db.get_redis_db())


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def read_root():
    return {"message": "Hello World"}


if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)
