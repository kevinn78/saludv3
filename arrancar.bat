@echo off
title Lanzador de Proyecto - Salud Mental v3
echo =======================================================
echo   🚀 INICIANDO ECOSISTEMA DE SALUD MENTAL AUTOMATIZADO
echo =======================================================
echo.

:: 1. Verificar Entorno Virtual
if not exist ".venv\Scripts\python.exe" (
    echo ❌ ERROR: No se detectó el entorno virtual .venv.
    echo Por favor asegúrate de instalar las dependencias primero.
    pause
    exit
)

:: 2. Ejecutar el Pipeline ETL
echo 📥 [1/3] Ejecutando Pipeline ETL para actualizar base de datos...
.venv\Scripts\python.exe -m etl.main
if %errorlevel% neq 0 (
    echo ❌ ERROR en el ETL. Revisa los datos de origen.
    pause
    exit
)
echo  Verificado con éxito.
echo.

:: 3. Levantar la API RESTful (Uvicorn) en segundo plano
echo 🔌 [2/3] Levantando API RESTful de FastAPI (Puerto 8000)...
start /b "" .venv\Scripts\python.exe -m uvicorn api.main:app --port 8000

:: Darle 3 segundos a la API para que despierte antes de lanzar el frontend
timeout /t 3 /nobreak >nul

:: 4. Lanzar el Frontend Interactivo (Streamlit)
echo 📊 [3/3] Lanzando Dashboard de Streamlit en el navegador...
echo.
echo =======================================================
echo   🎉 ¡Todo listo! Mantén esta ventana abierta.
echo   Presiona CTRL+C en esta consola si deseas apagar todo.
echo =======================================================
echo.
.venv\Scripts\python.exe -m streamlit run dashboards/main.py

pause