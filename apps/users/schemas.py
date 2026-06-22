from ninja import Schema
from pydantic import model_validator

class UserSchema(Schema):
    id: int
    username: str
    email: str
    role: str

class RegisterSchema(Schema):
    username: str
    email: str
    password: str
    password_confirm: str

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self

class LoginSchema(Schema):
    username: str
    password: str

class TokenSchema(Schema):
    access: str
    refresh: str

class RefreshSchema(Schema):
    refresh: str
