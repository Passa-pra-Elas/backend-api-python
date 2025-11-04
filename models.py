from pydantic import BaseModel
from typing import *

class X_template(BaseModel):
    left: float = None
    right: float = None
class Y_template(BaseModel):
    up: float = None
    down : float = None
class CreatePerimeterDTO(BaseModel):
    name: str
    x: X_template
    y: Y_template
class UpdatePerimeterDTO(BaseModel):
    id: str
    name: Optional[str] = None
    x: Optional[X_template] = None
    y: Optional[Y_template] = None

class ChoosePerimeterDTO(BaseModel):
    id: str

print()