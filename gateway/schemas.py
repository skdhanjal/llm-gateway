from pydantic import BaseModel, Field, field_validator

class CompanyFacts(BaseModel):
    """Extraction worksheet — field order IS generation order."""
    reasoning: str = Field(
        description="One sentence: where in the text each fact was found.")
    name: str
    sector: str
    employees: int = Field(description="Headcount as an integer.")
    founded_year: int | None = Field(
        description="Four-digit year, or null if not stated.")

    # Stage-2 semantics: the grammar cannot know these.
    @field_validator("employees")
    @classmethod
    def employees_positive(cls, v):
        if v <= 0: raise ValueError("employees must be positive")
        return v

    @field_validator("founded_year")
    @classmethod
    def year_sane(cls, v):
        if v is not None and not (1600 <= v <= 2026):
            raise ValueError("founded_year out of plausible range")
        return v

SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "company_facts": CompanyFacts,
}