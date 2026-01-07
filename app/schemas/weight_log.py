from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class WeightUpdateRequest(BaseModel):
    startingweight: Optional[Decimal] = None
    targetweight: Optional[Decimal] = None
    unit: Optional[str] = "kg"
