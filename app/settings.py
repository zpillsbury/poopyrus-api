from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongo_uri: str
    static_token: str
    google_project: str
    google_auth_pk: str
    google_auth_client_email: str
    google_auth_token_uri: str
    google_auth_sign_in_url: str = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    )
    google_auth_sign_in_key: str
    testing: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
