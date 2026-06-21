"""
This file handles data validation. It ensures that when your agents speak to each other, they use
strict, predictable data models.
"""

### schemas.py
from pydantic import BaseModel, Field

class DrinkSchema(BaseModel):
    drink_name: str = Field(description="The name of the recommended beverage")
    caffeine_level: str = Field(description="Caffeine category: High, Medium, or None.")

class ActivitySchema(BaseModel):
    paired_activity: str = Field(description="A simpel, conforing 2-minute activity.")
    rationale: str = Field(description="A friendly explanation of why this matches their mood.")

