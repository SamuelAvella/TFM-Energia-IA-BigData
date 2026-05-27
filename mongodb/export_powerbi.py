# ============================================================================
# EXPORTAR DESDE MONGODB A CSV PARA POWER BI
# ============================================================================
# Este script extrae snapshots de las 3 colecciones a CSV ubicados en
# powerbi/data/ para que el dashboard Power BI los consuma.
#
# En producción real, este paso lo sustituiría una conexión DirectQuery o
# un conector ODBC entre Power BI y MongoDB. Para el TFM se exportan
# snapshots por simplicidad operativa.
# ============================================================================

import pandas as pd
from pymongo import MongoClient
from pathlib import Path

MONGO_URI = "mongodb://admin:bigdataspark@localhost:27017/"
DB_NAME = "tfm_energia"

PROYECTO = Path(__file__).parent.parent
RUTA_SALIDA = PROYECTO / "powerbi" / "data"
RUTA_SALIDA.mkdir(parents=True, exist_ok=True)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

print(f"Exportando colecciones a: {RUTA_SALIDA}\n")

# ----------------------------------------------------------------------------
# 1. predicciones_clasificador
# ----------------------------------------------------------------------------
print("Exportando predicciones_clasificador...")
docs = list(db.predicciones_clasificador.find({}, {'_id': 0}))
df = pd.DataFrame(docs)
df.to_csv(RUTA_SALIDA / "predicciones_clasificador.csv", index=False)
print(f"  ✓ {len(df):,} filas → predicciones_clasificador.csv")

# ----------------------------------------------------------------------------
# 2. demanda_predicciones
# ----------------------------------------------------------------------------
print("\nExportando demanda_predicciones...")
docs = list(db.demanda_predicciones.find({}, {'_id': 0}))
df = pd.DataFrame(docs)
df.to_csv(RUTA_SALIDA / "demanda_predicciones.csv", index=False)
print(f"  ✓ {len(df):,} filas → demanda_predicciones.csv")

# ----------------------------------------------------------------------------
# 3. demanda_historica
# ----------------------------------------------------------------------------
print("\nExportando demanda_historica...")
docs = list(db.demanda_historica.find({}, {'_id': 0}))
df = pd.DataFrame(docs)
df.to_csv(RUTA_SALIDA / "demanda_historica.csv", index=False)
print(f"  ✓ {len(df):,} filas → demanda_historica.csv")

print("\n" + "="*60)
print("EXPORTACIÓN COMPLETADA")
print("="*60)
print(f"Power BI debe leer los CSV desde: {RUTA_SALIDA}")
print("="*60)

client.close()