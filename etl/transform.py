import logging
from pydantic import BaseModel, Field, field_validator

# 1. Configuración del Sistema de Logging Profesional (Exigencia de la rúbrica)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("etl_process.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# 2. Definición del esquema estricto para mapear y blindar tus datos
class ColaboradorSchema(BaseModel):
    age: int = Field(..., ge=15, le=100)
    gender: str
    employment_status: str
    work_environment: str
    mental_health_history: str
    seeks_treatment: str
    stress_level: int = Field(..., ge=0, le=10)
    sleep_hours: float = Field(..., ge=0.0, le=24.0)
    physical_activity_days: int = Field(..., ge=0, le=7)
    depression_score: int = Field(..., ge=0, le=30)
    anxiety_score: int = Field(..., ge=0, le=30)
    social_support_score: int = Field(..., ge=0, le=100)
    productivity_score: float = Field(..., ge=0.0, le=100.0)
    mental_health_risk: str
    Country: str
    Country_Code: str
    stress_category: str
    insufficient_sleep: int = Field(..., ge=0, le=1)
    mental_health_alert: int = Field(..., ge=0, le=1)

    # Regla personalizada para interceptar datos corruptos en el entorno laboral
    @field_validator("work_environment")
    @classmethod
    def validar_entorno_laboral(cls, value: str) -> str:
        entornos_validos = ["Remote", "On-site", "Hybrid"]
        if value not in entornos_validos:
            raise ValueError(f"El entorno '{value}' no pertenece a las categorías permitidas.")
        return value