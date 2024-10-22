from pydantic import BaseModel, field_validator
import re

class UserSchema(BaseModel):
    username: str
    password: str

    @field_validator("username")
    def validate_username(cls, value: str) -> str:
        if not re.match("^([a-z]|[0-9]|@)+$", value):
            raise ValueError("Username format inalid")
        return value 
