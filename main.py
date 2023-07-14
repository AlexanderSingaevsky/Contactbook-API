from fastapi import FastAPI
from src.contacts.routes import router as contacts
from src.phones.routes import router as phones
from src.emails.routes import router as emails
from src.auth.routes import router as auth

app = FastAPI()

app.include_router(auth, prefix='/api')
app.include_router(contacts, prefix='/api')
app.include_router(phones, prefix='/api')
app.include_router(emails, prefix='/api')


@app.get("/")
def read_root():
    return {"message": "Hello World"}
