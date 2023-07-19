from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.contacts.routes import router as contacts
from src.phones.routes import router as phones
from src.emails.routes import router as emails
from src.auth.routes import router as auth
from src.database_redis import redis_db

app = FastAPI()

origins = ["http://localhost:3000"]

app.include_router(auth, prefix='/api')
app.include_router(contacts, prefix='/api')
app.include_router(phones, prefix='/api')
app.include_router(emails, prefix='/api')
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await FastAPILimiter.init(await redis_db.get_redis_db())


@app.get("/", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def read_root():
    return {"message": "Hello World"}
