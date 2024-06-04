from pydantic import BaseModel


class OrmModel(BaseModel):
    """Generic for pydantic models"""

    class Config:
        orm_mode = True
