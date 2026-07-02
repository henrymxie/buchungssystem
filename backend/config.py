from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Diese Werte kommen aus der .env-Datei bzw. aus Umgebungsvariablen.
    # Die Angaben hier sind nur Fallback-Werte, falls nichts gesetzt ist.
    admin_username: str = "admin"
    admin_password: str = "admin123"
    user_username: str = "user"
    user_password: str = "user123"
    auto_seed: bool = False

    # Sagt pydantic-settings: lies zusätzlich eine .env-Datei ein.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Einmal erzeugen, überall importierbar.
settings = Settings()