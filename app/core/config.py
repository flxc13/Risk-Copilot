from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Risk Copilot"
    app_env: str = "dev"
