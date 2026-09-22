from pydantic import BaseModel


class ClientOut(BaseModel):
    id: int
    name: str
    country_code: str

    model_config = {"from_attributes": True}


class ChartPoint(BaseModel):
    period: str
    year: int
    value: float


class DashboardSummary(BaseModel):
    total_client_count: int
    selected_client_id: int | None
    headcount_series: list[ChartPoint]
    total_gross_series: list[ChartPoint]
    employer_cost_series: list[ChartPoint]
