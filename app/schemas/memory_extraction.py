# Schema for the LLM to decide WHAT to save
from pydantic import BaseModel, Field


class MemoryExtraction(BaseModel):
    important_fact: str | None = Field(None, description="Extract a standalone fact if the user mentioned a name, preference, or life detail. Else None.")
    category: str = Field("general", description="Category: 'identity', 'preference', 'family', 'work'")
