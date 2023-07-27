import secrets

from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail
from pydantic import EmailStr
from fastapi_mail import MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors

from src.config import settings as s
from src.auth.service import auth_service


class FastMailService:
    conf = ConnectionConfig(
        MAIL_USERNAME=s.mail_username,
        MAIL_PASSWORD=s.mail_password,
        MAIL_FROM=s.mail_from,
        MAIL_PORT=s.mail_port,
        MAIL_SERVER=s.mail_server,
        MAIL_FROM_NAME=s.mail_from_name,
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER=Path(__file__).parent.parent.parent / 'templates',
    )

    def __init__(self):
        self.mf = FastMail(self.conf)

    async def send_verification_email(self, email: EmailStr, username: str, host: str):
        try:
            token_verification = await auth_service.create_email_token({"sub": email})
            message = MessageSchema(
                subject="Confirm your email ",
                recipients=[email],
                template_body={"host": host, "username": username, "token": token_verification},
                subtype=MessageType.html
            )

            await self.mf.send_message(message, template_name="email_verification.html")
        except ConnectionErrors as err:
            print(err)

    async def send_password_reset_mail(self, email: EmailStr, username: str, host: str, reset_token: str):
        try:
            message = MessageSchema(
                subject="Reset your password",
                recipients=[email],
                template_body={"host": host, "username": username, "token": reset_token},
                subtype=MessageType.html
            )

            await self.mf.send_message(message, template_name="reset_password.html")

        except ConnectionErrors as err:
            print(err)


mail_service = FastMailService()
