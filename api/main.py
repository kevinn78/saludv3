import os
import sqlite3
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="API de Alertas de Salud Mental Organizacional")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE RUTAS DE BASE DE DATOS Y MODELOS ---
if os.path.exists("salud_mental.db"):
    DB_PATH = "salud_mental.db"
elif os.path.exists(os.path.join("data", "salud_mental.db")):
    DB_PATH = os.path.join("data", "salud_mental.db")
else:
    DB_PATH = "/app/salud_mental.db"

if os.path.exists(os.path.join("models", "clasificador_alerta.joblib")):
    PATH_CLASIFICADOR = os.path.join("models", "clasificador_alerta.joblib")
    PATH_REGRESOR = os.path.join("models", "regresor_productividad.joblib")
else:
    PATH_CLASIFICADOR = "/app/models/clasificador_alerta.joblib"
    PATH_REGRESOR = "/app/models/regresor_productividad.joblib"

# --- ESQUEMAS PYDANTIC (VALIDACIÓN DE ENTRADA Y SALIDA) ---
class DatosPrediccion(BaseModel):
    age: int = Field(..., example=35, description="Edad del colaborador")
    stress_level: int = Field(..., example=7, description="Nivel de estrés percibido (1-10)")

class MetricasColaboradorOut(BaseModel):
    age: int
    stress_level: float
    productivity_score: float
    Country: str
    mental_health_alert: int

    class Config:
        from_attributes = True 

# --- FUNCIÓN AUXILIAR SQLITE ---
def ejecutar_consulta_db(query, args=()):
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Base de datos relacional no encontrada.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    cursor.execute(query, args)
    resultados = cursor.fetchall()
    conn.close()
    return [dict(fila) for fila in resultados]

# --- ENDPOINTS ANALÍTICOS (TIPADOS PARA SWAGGER) ---

@app.get("/api/v1/metrics/macro", response_model=list[MetricasColaboradorOut])
def obtener_metricas_gerenciales():
    """Endpoint optimizado para la Vista Gerencial Macro"""
    query = "SELECT age, stress_level, productivity_score, Country, mental_health_alert FROM alertas_salud_mental"
    return ejecutar_consulta_db(query)

@app.get("/api/v1/alerts/critical", response_model=list[MetricasColaboradorOut])
def obtener_casos_criticos():
    """Endpoint optimizado para la Vista Operativa Granular (Recursos Humanos)"""
    query = "SELECT age, stress_level, productivity_score, Country, mental_health_alert FROM alertas_salud_mental WHERE mental_health_alert = 1"
    return ejecutar_consulta_db(query)

# --- ENDPOINTS PREDICTIVOS (INTELIGENCIA ARTIFICIAL) ---

@app.post("/api/v1/predict/alert")
def predecir_alerta_salud(datos: DatosPrediccion):
    """Endpoint que predice en tiempo real si un colaborador requiere alerta de salud mental (0 o 1)"""
    if not os.path.exists(PATH_CLASIFICADOR):
        raise HTTPException(status_code=500, detail="Modelo clasificador no encontrado. Ejecute entrenar.py primero.")
    
    try:
        modelo = joblib.load(PATH_CLASIFICADOR)
        features = [[datos.age, datos.stress_level]]
        
        prediccion = modelo.predict(features)[0]
        probabilidad = modelo.predict_proba(features)[0][1] if hasattr(modelo, "predict_proba") else None
        
        return {
            "status": "success",
            "mental_health_alert_prediction": int(prediccion),
            "risk_probability": float(probabilidad) if probabilidad is not None else "N/A"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la inferencia: {str(e)}")

@app.post("/api/v1/predict/productivity")
def predecir_score_productividad(datos: DatosPrediccion):
    """Endpoint que predice el Score de Productividad numérico esperado de un colaborador"""
    if not os.path.exists(PATH_REGRESOR):
        raise HTTPException(status_code=500, detail="Modelo regresor no encontrado. Ejecute entrenar.py primero.")
    
    try:
        modelo = joblib.load(PATH_REGRESOR)
        features = [[datos.age, datos.stress_level]]
        
        prediccion_continua = modelo.predict(features)[0]
        
        return {
            "status": "success",
            "predicted_productivity_score": round(float(prediccion_continua), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la inferencia: {str(e)}")