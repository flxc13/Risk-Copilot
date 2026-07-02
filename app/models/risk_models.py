from pydantic import BaseModel


class PortfolioRiskSnapshot(BaseModel):
    portfolio_id: str
    var_95: float
