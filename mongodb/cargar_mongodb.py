# ============================================================================
# CARGA DE DATOS EN MONGODB
# ============================================================================
# Vuelca 3 colecciones al MongoDB del proyecto:
#   - predicciones_clasificador  (salida del clasificador RapidMiner)
#   - demanda_predicciones        (salida del LSTM)
#   - demanda_historica           (serie histórica REData)
# ============================================================================

import pandas as pd
from pymongo import MongoClient
from pathlib import Path

# --- Configuración ----------------------------------------------------------
MONGO_URI = "mongodb://admin:bigdataspark@localhost:27017/"
DB_NAME = "tfm_energia"

PROYECTO = Path(__file__).parent.parent

RUTA_PREDICCIONES_CLASIFICADOR = PROYECTO / "rapidminer" / "data" / "predicciones_clasificador.csv"
RUTA_PREDICCIONES_LSTM         = PROYECTO / "lstm" / "data" / "predicciones_lstm.csv"
RUTA_DEMANDA_HISTORICA         = PROYECTO / "volumes" / "hdfs" / "features" / "demanda_clean.csv"

print(f"Conectando a MongoDB en {MONGO_URI}...")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
print(f"✓ Conectado a base de datos: {DB_NAME}\n")


# ============================================================================
# COLECCIÓN 1: predicciones_clasificador
# ============================================================================
print("="*60)
print("COLECCIÓN: predicciones_clasificador")
print("="*60)

df = pd.read_csv(RUTA_PREDICCIONES_CLASIFICADOR)
print(f"Origen: {RUTA_PREDICCIONES_CLASIFICADOR.name}")
print(f"Filas:  {len(df):,}, Columnas: {len(df.columns)}")

# Limpiamos nombres de columnas (RapidMiner mete paréntesis y espacios)
df.columns = (
    df.columns
    .str.replace('(', '_', regex=False)
    .str.replace(')', '', regex=False)
    .str.replace(' ', '_', regex=False)
    .str.lower()
)
print(f"Columnas normalizadas: {list(df.columns)}")

registros = df.to_dict(orient='records')

db.predicciones_clasificador.drop()
db.predicciones_clasificador.insert_many(registros)
db.predicciones_clasificador.create_index("cons_no")
db.predicciones_clasificador.create_index("prediction_flag")

print(f"✓ Insertados {db.predicciones_clasificador.count_documents({}):,} documentos")
print(f"✓ Índices: cons_no, prediction_flag\n")


# ============================================================================
# COLECCIÓN 2: demanda_predicciones (LSTM)
# ============================================================================
print("="*60)
print("COLECCIÓN: demanda_predicciones")
print("="*60)

df = pd.read_csv(RUTA_PREDICCIONES_LSTM, parse_dates=['timestamp'])
print(f"Origen: {RUTA_PREDICCIONES_LSTM.name}")
print(f"Filas:  {len(df):,}")

registros = df.to_dict(orient='records')

db.demanda_predicciones.drop()
db.demanda_predicciones.insert_many(registros)
db.demanda_predicciones.create_index("timestamp")

print(f"✓ Insertados {db.demanda_predicciones.count_documents({}):,} documentos")
print(f"✓ Índice: timestamp\n")


# ============================================================================
# COLECCIÓN 3: demanda_historica
# ============================================================================
print("="*60)
print("COLECCIÓN: demanda_historica")
print("="*60)

df = pd.read_csv(RUTA_DEMANDA_HISTORICA, parse_dates=['timestamp'])
print(f"Origen: {RUTA_DEMANDA_HISTORICA.name}")
print(f"Filas:  {len(df):,}")

registros = df.to_dict(orient='records')

db.demanda_historica.drop()
db.demanda_historica.insert_many(registros)
db.demanda_historica.create_index("timestamp")

print(f"✓ Insertados {db.demanda_historica.count_documents({}):,} documentos")
print(f"✓ Índice: timestamp\n")


# ============================================================================
# RESUMEN
# ============================================================================
print("="*60)
print("RESUMEN CARGA MONGODB")
print("="*60)
print(f"Base de datos: {DB_NAME}")
print(f"Colecciones:")
for col in sorted(db.list_collection_names()):
    n = db[col].count_documents({})
    print(f"  - {col:30s}  {n:>10,} documentos")
print("="*60)
print("\n✓ Carga completada.")

client.close()