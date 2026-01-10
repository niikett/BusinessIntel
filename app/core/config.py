from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(".env", override=True)

class Settings(BaseSettings):
    database_url: str

    requests_per_hour: int
    delay_between_requests: int
    max_concurrent_requests: int

    log_level: str
    log_file: str

    scheduler_enabled: bool
    daily_crawl_time: str
    weekly_report_day: str  
    weekly_report_time: str

    min_opportunity_score: float
    auto_export_reports: bool

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env",
        env_file_encoding = "utf-8"
    )

    @property
    def database_url(self):
        return self.database_url

settings = Settings()

