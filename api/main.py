import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API de Alertas de Salud Mental Organizacional")

# Permitir que el Dashboard se conecte sin bloqueos de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("salud_mental.db"):
    DB_PATH = "salud_mental.db"
elif os.path.exists(os.path.join("data", "salud_mental.db")):
    DB_PATH = os.path.join("data", "salud_mental.db")
else:
    DB_PATH = "/app/salud_mental.db"

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

@app.get("/api/v1/metrics/macro")
def obtener_metricas_gerenciales():
    """Endpoint optimizado para la Vista Gerencial Macro"""
    query = "SELECT age, stress_level, productivity_score, Country, mental_health_alert FROM alertas_salud_mental"
    return ejecutar_consulta_db(query)

@app.get("/api/v1/alerts/critical")
def obtener_casos_criticos():
    """Endpoint optimizado para la Vista Operativa Granular (Recursos Humanos)"""
    query = "SELECT * FROM alertas_salud_mental WHERE mental_health_alert = 1"
    return ejecutar_consulta_db(query)