import uvicorn
from fastapi import BackgroundTasks, APIRouter
from fastapi_mail import FastMail, MessageSchema,MessageType

from src.mailing.schemas import EmailSchema
from src.mailing.service import mail_service

router = APIRouter(prefix='/mailing', tags=["mailing"])


@router.post("/send-email")
async def send_in_background(background_tasks: BackgroundTasks, body: EmailSchema):
    message = MessageSchema(
        subject="Fastapi mail module",
        recipients=[body.email],
        template_body={"fullname": "Billy Jones"},
        subtype=MessageType.html
    )

    fm = mail_service.get_service()

    background_tasks.add_task(fm.send_message, message, template_name="example_email.html")

    return {"message": "email has been sent"}


if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)

