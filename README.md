# Sistema Analítico de Salud Mental Organizacional (v3)

Este proyecto implementa un ecosistema de Business Intelligence e Ingeniería de Datos de extremo a extremo (End-to-End). El sistema procesa información de bienestar laboral de 7.929 colaboradores, centraliza las métricas mediante una arquitectura de servicios y las disponibiliza en un entorno interactivo multifuncional.

---

##  Arquitectura del Sistema

El flujo de datos está compuesto por las siguientes capas acopladas:
1. **Pipeline ETL (`etl/`):** Extracción automatizada, limpieza, validación de esquemas y carga/persistencia en una base de datos relacional local (`salud_mental.db` usando SQLite).
2. **API RESTful (`api/`):** Backend desarrollado con **FastAPI** y servidor **Uvicorn** que expone endpoints optimizados para el consumo granular y macro de las métricas de salud laboral.
3. **Dashboard Interactivo (`dashboards/`):** Frontend dinámico construido en **Streamlit** que utiliza **Plotly Express** para renderizar 5 gráficos interactivos con filtros globales cruzados (Distribución de estrés, puestos de trabajo, estado civil completo, correlación de productividad y mapa operativo de alertas críticas).

---

##  Instrucciones de Ejecución Rápida (Windows)

Para que el proyecto funcione de forma completamente automatizada en cualquier equipo sin necesidad de configurar terminales independientes, sigue estos pasos:

### 1. Prerrequisitos
Asegúrate de tener instalado **Python 3.11** (o superior) y agregarlo al PATH del sistema operativo.

### 2. Instalación Única de Dependencias
Abre una terminal (PowerShell o CMD) en la raíz de la carpeta del proyecto y ejecuta el siguiente comando para montar las librerías necesarias en tu entorno virtual:
```bash
pip install -r requirements.txt


```
### 3. Correr Dashboard
Abre una terminal (PowerShell o CMD) en la raíz de la carpeta del proyecto y ejecuta el siguiente comando :
---

arrancar.bat
