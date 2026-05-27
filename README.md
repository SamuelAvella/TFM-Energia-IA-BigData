# TFM Energía · Big Data + IA aplicada al sector eléctrico

**Autor:** Samuel Avella Pérez
**Máster:** Especialización en IA y Big Data — DigitechFP — 2025/2026

## Resumen
Plataforma Big Data que integra:
- Clasificador de fraude eléctrico (Gradient Boosted Trees, RapidMiner) — AUC 0.775
- LSTM de predicción de demanda a 48h (PyTorch + GPU) — MAPE 3.48%
- Persistencia en MongoDB y visualización en Power BI

## Estructura

```text
TFM-Energia-IA&BigData/
├── .venv/                          # Entorno virtual Python (local)
├── .gitignore                      # Archivos y carpetas excluidos de Git
├── README.md                       # Documentación principal del proyecto
├── docker-compose.yaml             # Despliegue del clúster Spark Standalone
├── info.txt                        # Notas auxiliares de configuración
│
├── docs/                           # Documentación del TFM
│   └── capturas/                   # Capturas de pantalla e imágenes para la memoria
│
├── volumes/                        # Data Lake local del clúster de Big Data
│   ├── compute-bigdata/            # Espacio de computación analítica (PySpark)
│   │   └── tfm/notebooks/          # Pipeline de ingeniería de datos y análisis
│   │       ├── 01_exploracion_sgcc.ipynb
│   │       ├── 02_limpieza_sgcc.ipynb
│   │       ├── 03_features_sgcc.ipynb
│   │       ├── 04_descarga_redata.ipynb
│   │       └── 05_etl_demanda.ipynb
│   └── hdfs/                       # Sistema de archivos distribuido simulado (Raw, Processed, Features)
│
├── rapidminer/                     # Módulo de Clasificación de Fraude Eléctrico
│   ├── data/                       # Datasets de entrada y salida de las predicciones
│   │   ├── sgcc_features.csv
│   │   └── predicciones_clasificador.csv
│   ├── process/                    # Procesos analíticos de RapidMiner
│   │   └── 01_clasificador_fraude.rmp
│   └── process.png                 # Diagrama visual del flujo de datos en RapidMiner
│
├── lstm/                           # Modelo de Redes Neuronales para Predicción de Demanda
│   ├── data/                       # Series temporales históricas y resultados obtenidos
│   │   ├── demanda_clean.csv
│   │   └── predicciones_lstm.csv
│   ├── notebooks/                  # Modelado predictivo (Entrenamiento local + GPU)
│   │   ├── 01_eda_demanda.ipynb
│   │   ├── 02_baseline_naive.ipynb
│   │   └── 03_lstm_pytorch.ipynb
│   ├── model/                      # Artefactos del modelo entrenado y serializadores
│   │   ├── lstm_demanda.pt
│   │   └── scalers.pkl
│   ├── requirements.txt            # Dependencias del entorno de Deep Learning
│   ├── resultados_baseline.json    # Métricas del modelo base (Naive)
│   └── resultados_lstm.json        # Métricas del modelo predictivo LSTM
│
├── mongodb/                        # Capa NoSQL Operacional
│   ├── data/                       # Volumen persistente para la base de datos Mongo
│   ├── docker-compose.yaml         # Orquestación del contenedor de MongoDB
│   ├── cargar_mongodb.py           # Script de ingesta de datos (Genera las 3 colecciones desde CSV)
│   └── export_powerbi.py           # Script de extracción y snapshot analítico para el Dashboard
│
└── powerbi/                        # Inteligencia de Negocio y Visualización
    ├── data/                       # Fuentes de datos optimizadas (CSV extraídos de Mongo)
    ├── panels/                     # Capturas de los dashboards interactivos para el reporte
    └── TFM.pbit                    # Plantilla de Power BI (fichero optimizado sin datos embebidos)
```

## Cómo reproducir

### Requisitos
- Docker Desktop
- Python 3.11 + venv
- GPU NVIDIA + CUDA 12+

### Paso 1: levantar el clúster Big Data
cd volumes && docker-compose up -d

### Paso 2: ejecutar los notebooks Spark (en orden)
01_exploracion_sgcc → 02_limpieza_sgcc → 03_features_sgcc
04_descarga_redata → 05_etl_demanda

### Paso 3: ejecutar los notebooks LSTM en VS Code
01_eda_demanda → 02_baseline_naive → 03_lstm_pytorch

### Paso 4: cargar MongoDB
cd mongodb && docker-compose up -d
python cargar_mongodb.py

### Paso 5: abrir el dashboard
Abrir powerbi/dashboard.pbix en Power BI Desktop

## Resultados

###  Clasificador de Fraude Eléctrico (Gradient Boosted Trees)
Tras evaluar cuatro algoritmos mediante **Cross Validation de 5-fold estratificado** y técnicas de sobremuestreo **SMOTE** integradas en el subproceso de entrenamiento, el modelo seleccionado fue **Gradient Boosted Trees**. 

La evaluación se realizó sobre un conjunto de test reservado que representa el **30% del dataset total (9.357 contadores independientes)** nunca vistos por el modelo durante el entrenamiento.

#### Métricas de Rendimiento
| Métrica | Valor | Estado / Observación |
| :--- | :---: | :--- |
| **AUC-ROC** | **0,775** | Mejora respecto al Cross Validation (0,766), descartando sobreajuste. |
| **Recall (Fraude)** | **65,84%** | El modelo es capaz de capturar **2 de cada 3 fraudes reales**. |
| **Precision (Fraude)** | **18,25%** | Ratio de acierto en alertas; balanceado para evitar fatiga de analistas. |
| **F1-Score** | **28,58%** | Media armónica balanceada bajo un escenario de alto desequilibrio. |
| **Accuracy** | **74,58%** | Porcentaje de acierto global sobre el conjunto de test. |
| **Specificity** | **75,31%** | Capacidad de cribado correcto de usuarios legítimos. |

#### Matriz de Confusión (N = 9.357)
| | Predicho Normal | Predicho Fraude |
| :--- | :---: | :---: |
| **Normal Real** | **6.502** | 2.132 *(Falsos Positivos)* |
| **Fraude Real** | 247 *(Falsos Negativos)* | **476** *(Verdaderos Positivos)* |

---

### Predicción de Demanda Eléctrica (LSTM)
La validación del modelo predictivo de Deep Learning se ejecutó bajo un escenario de **test temporal estricto** (período de enero a abril de 2026), evaluando un total de **2.663 ventanas de 48 horas**.

#### Comparativa de Modelos
| Métrica |  LSTM (PyTorch) | Baseline Naive Estacional | Mejora Relativa |
| :--- | :---: | :---: | :---: |
| **MAE (MW)** | **972,46** | 1.430,42 | **-32,01%** |
| **RMSE (MW)** | **1.275,82** | 2.332,27 | **-45,30%** |
| **MAPE** | **3,48%** | 5,11% | **-31,90%** |

#### Degradación del Error en el Horizonte de Predicción ($h$)
* **$h+1$ (Próxima hora):** **3,08%** de error (MAPE)
* **$h+24$ (Un día vista):** **3,26%** de error (MAPE)
* **$h+48$ (Dos días vista):** **4,00%** de error (MAPE)

## Licencia
MIT