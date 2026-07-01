from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    # App
    app_name: str = "GrantFlow AI"
    debug: bool = False
    secret_key: str

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_jwt_secret: str

    # Database (direct connection for SQLAlchemy/Alembic)
    database_url: str  # postgresql+asyncpg://...

    # AI
    anthropic_api_key: str
    openai_api_key: str

    # Redis
    redis_url: str

    # Stripe
    stripe_secret_key: str
    stripe_webhook_secret: str

    # Resend
    resend_api_key: str
    from_email: str = "noreply@grantflow.ai"

    # GrantConnect
    grantconnect_api_key: str = ""
    grantconnect_base_url: str = "https://www.grants.gov.au/api/v1"

    # App URL
    frontend_url: str = "http://localhost:3000"


settings = Settings()
