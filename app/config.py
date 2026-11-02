import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def _load_env_file(env_path: Path):
    """Simple parser for .env file if python-dotenv is not installed."""
    if not env_path.exists():
        return
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass

# Attempt to load local .env
_load_env_file(BASE_DIR / ".env")

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        PORT: int = int(os.getenv("PORT", "8000"))
        HOST: str = os.getenv("HOST", "0.0.0.0")
        DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

        LLM_API_KEY: str = os.getenv("LLM_API_KEY", "your_openai_or_gemini_api_key_here")
        LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
        LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))

        WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "your_meta_system_user_token_here")
        WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "your_whatsapp_phone_number_id_here")
        WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "your_custom_webhook_secret_verify_token_here")
        WHATSAPP_API_VERSION: str = os.getenv("WHATSAPP_API_VERSION", "v20.0")

        COMPANY_NAME: str = os.getenv("COMPANY_NAME", "Empório da Música")
        COMPANY_PHONE: str = os.getenv("COMPANY_PHONE", "+55 (11) 98765-4321")
        HUMAN_SUPPORT_PHONE: str = os.getenv("HUMAN_SUPPORT_PHONE", "+55 (11) 91234-5678")

        DATA_DIR: Path = BASE_DIR / "data"
        PRODUCTS_FILE: Path = BASE_DIR / "data" / "products.json"
        POLICIES_FILE: Path = BASE_DIR / "data" / "policies.json"
        ORDERS_FILE: Path = BASE_DIR / "data" / "orders.json"

        model_config = SettingsConfigDict(
            env_file=str(BASE_DIR / ".env"),
            env_file_encoding="utf-8",
            extra="ignore"
        )

    settings = Settings()

except ImportError:
    class StandaloneSettings:
        PORT: int = int(os.getenv("PORT", "8000"))
        HOST: str = os.getenv("HOST", "0.0.0.0")
        DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

        LLM_API_KEY: str = os.getenv("LLM_API_KEY", "your_openai_or_gemini_api_key_here")
        LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
        LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))

        WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "your_meta_system_user_token_here")
        WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "your_whatsapp_phone_number_id_here")
        WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "your_custom_webhook_secret_verify_token_here")
        WHATSAPP_API_VERSION: str = os.getenv("WHATSAPP_API_VERSION", "v20.0")

        COMPANY_NAME: str = os.getenv("COMPANY_NAME", "Empório da Música")
        COMPANY_PHONE: str = os.getenv("COMPANY_PHONE", "+55 (11) 98765-4321")
        HUMAN_SUPPORT_PHONE: str = os.getenv("HUMAN_SUPPORT_PHONE", "+55 (11) 91234-5678")

        DATA_DIR: Path = BASE_DIR / "data"
        PRODUCTS_FILE: Path = BASE_DIR / "data" / "products.json"
        POLICIES_FILE: Path = BASE_DIR / "data" / "policies.json"
        ORDERS_FILE: Path = BASE_DIR / "data" / "orders.json"

    settings = StandaloneSettings()
