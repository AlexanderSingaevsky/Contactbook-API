from pydantic import EmailStr, BaseModel


class EmailSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    new_password: str
    r_new_password: str
