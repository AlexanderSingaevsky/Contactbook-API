from pathlib import Path
from fastapi_mail import ConnectionConfig, FastMail

from src.config import settings as s


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
        self.mf = None

    async def get_service(self):
        if self.mf is None:
            self.mf = FastMail(self.conf)
        return self.mf


mail_service = FastMailService()
