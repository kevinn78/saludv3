import os
import sqlite3
import pandas as pd
from etl.transform import ColaboradorSchema, logging

DB_PATH = os.path.join("data", "salud_mental.db")
CSV_PATH = os.path.join("data", "Salud_Mental_Completo_Limpio.csv")

def inicializar_base_datos():
    """Crea la tabla SQL estructurada si no existe físicamente"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas_salud_mental (
            age INTEGER, gender TEXT, employment_status TEXT, work_environment TEXT,
            mental_health_history TEXT, seeks_treatment TEXT, stress_level INTEGER,
            sleep_hours REAL, physical_activity_days INTEGER, depression_score INTEGER,
            anxiety_score INTEGER, social_support_score INTEGER, productivity_score REAL,
            mental_health_risk TEXT, Country TEXT, Country_Code TEXT, stress_category TEXT,
            insufficient_sleep INTEGER, mental_health_alert INTEGER
        )
    """)
    conn.commit()
    conn.close()

def ejecutar_etl():
    logging.info(" [ETL] Iniciando el pipeline automatizado multifuente...")
    inicializar_base_datos()

    if not os.path.exists(CSV_PATH):
        logging.error(f"❌ [EXTRACT] Archivo CSV no encontrado en la ruta: {CSV_PATH}")
        return

    # 1. ETAPA DE EXTRACCIÓN (Extract)
    df_historico = pd.read_csv(CSV_PATH)
    logging.info(f" [EXTRACT] Dataset cargado exitosamente. Registros a procesar: {len(df_historico)}")
    
    # 2. ETAPA DE TRANSFORMACIÓN (Transform con validación fila por fila)
    registros_validados = []
    contador_errores = 0

    for indice, fila in df_historico.iterrows():
        try:
            datos_registro = fila.to_dict()
            # Forzamos a Pydantic a comprobar la consistencia de la fila
            registro_validado = ColaboradorSchema(**datos_registro)
            registros_validados.append(registro_validado.model_dump())
        except Exception as e:
            contador_errores += 1
            logging.warning(f" [TRANSFORM] Fila {indice} omitida por inconsistencia. Detalle: {e}")

    logging.info(f"📊 [TRANSFORM] Validación finalizada. Exitosos: {len(registros_validados)} | Errores omitidos: {contador_errores}")

    # 3. ETAPA DE CARGA (Load)
    try:
        conn = sqlite3.connect(DB_PATH)
        df_final = pd.DataFrame(registros_validados)
        
        # Limpiamos la tabla antes de cargar para evitar duplicar datos en fases de prueba
        conn.execute("DELETE FROM alertas_salud_mental")
        
        # Persistencia masiva indexada en SQL
        df_final.to_sql("alertas_salud_mental", conn, if_exists="append", index=False)
        conn.commit()
        conn.close()
        logging.info("[LOAD] Datos persistidos exitosamente en la Base de Datos SQL (salud_mental.db).")
    except Exception as e:
        logging.error(f"[LOAD] Error crítico al insertar datos en la base relacional: {e}")

if __name__ == "__main__":
    ejecutar_etl()