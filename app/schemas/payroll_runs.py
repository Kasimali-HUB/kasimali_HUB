from pydantic import BaseModel


class ImportResultOut(BaseModel):
    headcount: int
    total_gross: float
    employer_cost: float
    flagged_count: int


class PayrollRunOut(BaseModel):
    client_id: int
    client_name: str
    year: int
    period: str
