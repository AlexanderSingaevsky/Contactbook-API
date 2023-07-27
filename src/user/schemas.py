from pydantic import BaseModel


class NewPasswordSchema(BaseModel):
    current_password: str = "Current password"
    new_password: str = "New password"
    r_new_password: str = "Repeat new password"
