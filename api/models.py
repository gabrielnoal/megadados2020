from pydantic import BaseModel, Field, Extra
from typing import Optional, Dict

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

    class Config:
        extra = Extra.forbid
        schema_extra = {
            'example': {
                'description': 'Buy baby diapers',
                'completed': False,
            }
        }

