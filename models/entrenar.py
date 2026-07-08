import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    mean_squared_error, 
    r2_score, 
    precision_score, 
    recall_score, 
    f1_score
)
import joblib

# Configuración de rutas (híbrido local/Docker)
DB_PATH = "/app/salud_mental.db" if os.path.exists("/app/salud_mental.db") else os.path.join("data", "salud_mental.db")
MODELS_DIR = "models"

def cargar_datos():
    """Conecta a la base de datos relacional y extrae la data en un DataFrame"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"No se encontró la base de datos en: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    # Extraemos las columnas necesarias para el análisis predictivo
    query = "SELECT age, stress_level, productivity_score, Country, mental_health_alert FROM alertas_salud_mental"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def entrenar_ecosistema_ml():
    print("Inicializando Pipeline de Machine Learning para Ciencia de Datos...")
    df = cargar_datos()
    
    # -------------------------------------------------------------------------
    # OPTIMIZACIÓN Y TRANSFORMACIONES AVANZADAS (Pandas Vectorizado)
    # -------------------------------------------------------------------------
    # Optimizamos el uso de memoria RAM convirtiendo tipos de datos nativos
    df['Country'] = df['Country'].astype('category')
    
    # Definición de variables para los pipelines de Scikit-learn
    features_clasificacion = ['age', 'stress_level', 'productivity_score', 'Country']
    features_regresion = ['age', 'stress_level', 'Country'] # No incluimos productivity ya que es el target
    
    # Transformadores preprocesamiento (StandardScaler y OneHotEncoder)
    preprocesamiento = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), ['age', 'stress_level']),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['Country'])
        ],
        remainder='passthrough'
    )

    # =========================================================================
    # 1. MODELO DE CLASIFICACIÓN (Target: mental_health_alert)
    # =========================================================================
    print("\nEntrenando Modelo de Clasificación (Random Forest)...")
    X_c = df[features_clasificacion]
    y_c = df['mental_health_alert']
    
    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_c, y_c, test_size=0.2, random_state=42, stratify=y_c)
    
    pipeline_clasificador = Pipeline([
        ('preprocesamiento', preprocesamiento),
        ('modelo', RandomForestClassifier(random_state=42))
    ])
    
    # Optimización de Hiperparámetros mediante Validación Cruzada (GridSearchCV)
    parametros_c = {
        'modelo__n_estimators': [50, 100],
        'modelo__max_depth': [None, 10]
    }
    grid_c = GridSearchCV(pipeline_clasificador, parametros_c, cv=3, scoring='f1', n_jobs=-1)
    grid_c.fit(X_train_c, y_train_c)
    
    # Evaluación del clasificador
    pred_c = grid_c.predict(X_test_c)
    print(" Clasificador entrenado con éxito.")
    print("\n--- MÉTRICAS DE NEGOCIO (CLASIFICACIÓN) ---")
    print(classification_report(y_test_c, pred_c))
    print("Matriz de Confusión:")
    print(confusion_matrix(y_test_c, pred_c))
    
    # Guardar modelo serializado
    joblib.dump(grid_c.best_estimator_, os.path.join(MODELS_DIR, "clasificador_alerta.joblib"))

    # =========================================================================
    # 2. MODELO DE REGRESIÓN (Target: productivity_score)
    # =========================================================================
    print("\nEntrenando Modelo de Regresión (Linear Regression)...")
    # Para el preprocesamiento del regresor, ajustamos el ColumnTransformer para excluir columnas que no van
    preprocesamiento_r = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), ['age', 'stress_level']),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['Country'])
        ]
    )
    
    X_r = df[features_regresion]
    y_r = df['productivity_score']
    
    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X_r, y_r, test_size=0.2, random_state=42)
    
    pipeline_regresor = Pipeline([
        ('preprocesamiento', preprocesamiento_r),
        ('modelo', LinearRegression())
    ])
    
    pipeline_regresor.fit(X_train_r, y_train_r)
    
    # Evaluación del regresor
    pred_r = pipeline_regresor.predict(X_test_r)
    print("✅ Regresor entrenado con éxito.")
    print("\n📊 --- MÉTRICAS DE NEGOCIO (REGRESIÓN) ---")
    print(f"MSE (Error Cuadrático Medio): {mean_squared_error(y_test_r, pred_r):.2f}")
    print(f"R² (Coeficiente de Determinación): {r2_score(y_test_r, pred_r):.2f}")
    
    # Guardar modelo serializado
    joblib.dump(pipeline_regresor, os.path.join(MODELS_DIR, "regresor_productividad.joblib"))
    print("\n💾 ¡Modelos serializados correctamente en la carpeta /models/!")

if __name__ == "__main__":
    entrenar_ecosistema_ml()