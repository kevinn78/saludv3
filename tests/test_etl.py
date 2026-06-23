import sys
import os
from pydantic import ValidationError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from etl.transform import ColaboradorSchema

def test_esquema_pydantic_acepta_valores_correctos():
    datos_sanos = {
        "age": 28, "gender": "Female", "employment_status": "Employed", "work_environment": "Remote",
        "mental_health_history": "No", "seeks_treatment": "Yes", "stress_level": 4, "sleep_hours": 8.0,
        "physical_activity_days": 4, "depression_score": 12, "anxiety_score": 8, "social_support_score": 90,
        "productivity_score": 92.5, "mental_health_risk": "Low", "Country": "Chile", "Country_Code": "CL",
        "stress_category": "Bajo", "insufficient_sleep": 0, "mental_health_alert": 0
    }
    colaborador = ColaboradorSchema(**datos_sanos)
    assert colaborador.work_environment == "Remote"
    assert colaborador.age == 28
def test_esquema_pydantic_rechaza_valores_invalidos():
    datos_corruptos = {
        "age": 28, "gender": "Female", "employment_status": "Employed", 
        "work_environment": "In_The_Moon",
        "mental_health_history": "No", "seeks_treatment": "Yes", "stress_level": 4, "sleep_hours": 8.0,
        "physical_activity_days": 4, "depression_score": 12, "anxiety_score": 8, "social_support_score": 90,
        "productivity_score": 92.5, "mental_health_risk": "Low", "Country": "Chile", "Country_Code": "CL",
        "stress_category": "Bajo", "insufficient_sleep": 0, "mental_health_alert": 0
    }
    try:
        ColaboradorSchema(**datos_corruptos)
        assert False
    except ValidationError:
        assert True
