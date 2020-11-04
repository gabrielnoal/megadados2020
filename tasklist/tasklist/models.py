# pylint: disable=missing-module-docstring,missing-class-docstring
from typing import Optional

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from uuid import uuid4, UUID

# pylint: disable=too-few-public-methods
class Task(BaseModel):
    description: Optional[str] = Field(
        'no description',
        title='Task description',
        max_length=1024,
    )
    completed: Optional[bool] = Field(
        False,
        title='Shows whether the task was completed',
    )
    user_uuid: Optional[str] = Field(
        None,
        title='Task owner id',
    )
    

    class Config:
        schema_extra = {
            'example': {
                'description': 'Buy baby diapers',
                'completed': False,
                'user_uuid': None
            }
        }

class User(BaseModel):
    name: Optional[str] = Field(
        'no name',
        title='user name',
        max_length=1024,
    )
    user_uuid: str = Field(
        None,
        title='user id',
    )

    class Config:
        schema_extra = {
            'example': {
                'name': 'Nome',
                'user_uuid': uuid4(),
            }
        }
