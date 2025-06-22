import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from unidecode import unidecode

#Leer el archivo CSV original
obras = pd.read_csv('observatorio-de-obras-urbanas.csv', sep=';', encoding='latin1')


#----------------------------------------- Limpieza de datos -----------------------------------------
#Mostrar nombres de columnas y tipos.
print("Columnas")
print(obras.columns)
print("\nTipos de datos:")
print(obras.dtypes)

#chequeo de las columnas antes de la limpieza
#eliminación de acentos en las columnas de texto
print("\nPrimeras filas del DataFrame:")
print(obras.head(5))

for col in obras.columns:
    if col in ["entorno", "nombre", "etapa", "tipo", "area_responsable", "descripcion", "barrio", "direccion", "licitacion_oferta_empresa", 
                "contratacion_tipo", "nro_contratacion", "cuit_contratista", "expediente_numero", "financiamiento"]:
        obras[col] = obras[col].astype(str).apply(unidecode)

#----------------------------------------- Eliminación de Columnas -----------------------------------------
#Eliminar columnas "UNNAMED" al final del archivo
obras = obras.loc[:, ~obras.columns.str.startswith("Unnamed")]

print("\nPrimeras filas luego de eliminar columnas innecesarias:")
print(obras.columns)
print(obras.dtypes)

#Eliminar columnas que no se necesitan para el análisis.
#Estas columnas no aportan información relevante para el análisis de obras urbanas.
columnas_a_eliminar = [
            "imagen_2", "imagen_3", "imagen_4", "beneficiarios", "compromiso", "ba_elige", "link_interno", "pliego_descarga", "estudio_ambiental_descarga"
        ]
obras.drop(columns=columnas_a_eliminar, inplace=True, errors="ignore")


print("Columnas utiles que quedan:")
print(obras.columns)

#--------------------------- Limpieza de renglones repetidos ------------------

duplicados = obras[obras.duplicated(keep=False)]
print(duplicados)

# Eliminar filas duplicadas, conservando solo la primera aparición
obras = obras.drop_duplicates(keep='first')

#--------------------------- Unificar formato para columna "MONTO_CONTRATO" ----------------------------

print("\nEjemplos originales de monto_contrato:")
print(obras["monto_contrato"].head(10))

# Convertir a string y eliminar espacios en blanco 
obras["monto_contrato"] = obras["monto_contrato"].astype(str).str.strip()
#Elimina simbolo de pesos y espacios
obras["monto_contrato"] = obras["monto_contrato"].str.replace(r"[\$\s]", "", regex=True)
# Eliminar solo los puntos de los miles (antes de la coma)
obras["monto_contrato"] = obras["monto_contrato"].str.replace(".", "", regex=False)
obras["monto_contrato"] = obras["monto_contrato"].str.replace(",", ".", regex=False)
#Convertir a float
obras["monto_contrato"] = pd.to_numeric(obras["monto_contrato"], errors='coerce')
#Redondear a 2 decimales
#obras["monto_contrato"] = obras["monto_contrato"].round(2)

print("\nMonto_contrato ya limpio y como número:")
print(obras["monto_contrato"].head(10))


# --------------------------- Limpieza y formateo de TODAS las columnas que contienen "fecha" ----------------------------

#Columna "FECHA_INICIO"
print("\nEjemplos originales de FECHA_INICIO:")
print(obras["fecha_inicio"].head(10))
print(obras["fecha_fin_inicial"].head(10))

obras["fecha_inicio"] = pd.to_datetime(obras["fecha_inicio"], errors="coerce")

obras["fecha_fin_inicial"] = pd.to_datetime(obras["fecha_fin_inicial"], errors="coerce")

print("\nfecha_fin_inicial limpia y formateada:")
print(obras["fecha_inicio"].head(20))
print(obras["fecha_fin_inicial"].head(10))


#--------------------------- Limpieza de columna PLAZO_MESES ----------------------------
print("\nEjemplos originales de PLAZO_MESES:")
print(obras["plazo_meses"].head(30))

# Limpiar la columna "plazo_meses" y dejar solo enteros
obras["plazo_meses"] = obras["plazo_meses"].replace(
    ["", "A/D", "a/d", "s/d", "S/D", "Sin dato", "SIN DATO", None], np.nan
)
obras["plazo_meses"] = pd.to_numeric(obras["plazo_meses"], errors="coerce")
obras["plazo_meses"] = np.ceil(obras["plazo_meses"])
obras["plazo_meses"] = obras["plazo_meses"].astype('Int64') #Permite nulos


print("\nPlazo_meses limpio, redondeado hacia arriba:")
print(obras["plazo_meses"].head(30))


#--------------------------- Limpieza de columna PORCENTAJE_AVANCE ----------------------------

print("\nEjemplos originales de PORCENTAJE_AVANCE:")
print(obras["porcentaje_avance"].head(30))

# Reemplazar espacios en blanco por nulos 
obras["porcentaje_avance"] = obras["porcentaje_avance"].replace(["", " "], np.nan)

# Eliminar símbolos como "%" y convertir a número entero
obras["porcentaje_avance"] = obras["porcentaje_avance"].astype(str).str.replace("%", "", regex=False)
obras["porcentaje_avance"] = pd.to_numeric(obras["porcentaje_avance"], errors="coerce")


print("\nColumna PORCENTAJE_AVANCE limpia:")
print(obras["porcentaje_avance"].head(30))

#--------------------------- Limpieza de columna LICITACION_ANIO ----------------------------

print("\nEjemplos originales de LICITACION_ANIO:")
print(obras["licitacion_anio"].head(30))

# Reemplazar espacios vacíos por nulos 
obras["licitacion_anio"] = obras["licitacion_anio"].replace(["", " "], np.nan)
obras["licitacion_anio"] = pd.to_numeric(obras["licitacion_anio"], errors="coerce")
obras["licitacion_anio"] = obras["licitacion_anio"].astype('Int64')


print("\nColumna LICITACION_ANIO limpia:")
print(obras["licitacion_anio"].head(30))


#--------------------------- Limpieza de columna MANO_OBRA ----------------------------

print("\nEjemplos originales de MANO_OBRA:")
print(obras["mano_obra"].head(30))

obras["mano_obra"] = obras["mano_obra"].replace(["", " "], np.nan)
obras["mano_obra"] = pd.to_numeric(obras["mano_obra"], errors="coerce")
obras["mano_obra"] = obras["mano_obra"].astype('Int64')

print("\nColumna MANO_OBRA limpia:")
print(obras["mano_obra"].head(30))

#--------------------------- Limpieza de la columna DESTACADA -------------------------

print("\nEjemplos originales de DESTACADA: ")
print(obras["destacada"].head(20))

obras["destacada"] = obras["destacada"].astype(str).str.strip().str.upper()
obras["destacada"] = obras["destacada"].apply(lambda x:True if x == "SI" else False)

print("\nColumna DESTACADA limpia: ")
print(obras["destacada"].head(20))

#--------------------------- Limpieza de columna COMUNA ----------------------------

print("\nEjemplos originales de COMUNA:")
print(obras["comuna"].head(20))

obras["comuna"] = obras["comuna"].astype(str).str.strip().replace(["", " "], np.nan)
obras["comuna"] = pd.to_numeric(obras["comuna"], errors="coerce")
obras["comuna"] = obras["comuna"].astype('Int64')


print("\nColumna COMUNA limpia:")
print(obras["comuna"].head(30))


#--------------------------- Limpieza de columna BARRIO ----------------------------

print("\nEjemplos originales de BARRIO:")
print(obras["barrio"].head(20))

obras["barrio"] = obras["barrio"].astype(str).str.strip().str.lower()
obras["barrio"] = obras["barrio"].str.replace(r"\s+", " ", regex=True)
obras["barrio"] = obras["barrio"].replace(["", " "], pd.NA)


""" barrioVariantes = {                           #Esto reemplaza las variantes en la columna de barrios, pero hay que revisar uno a uno las diferentes opciones
    "villa urquiza": "villa urquiza",
    "villa urquiza ": "villa urquiza",
    "villa urquiza,": "villa urquiza",
    "villa lugano": "villa lugano",
    "villa lugano ": "villa lugano",
    "monserrat": "monserrat",
    "montserrat": "monserrat"
}
obras["barrios"] = obras["barrios"].replace(barrioVariantes) """


print("\nColumna COMUNA limpia:")
print(obras["comuna"].head(20))


#--------------------------- Limpieza de columna DIRECCION ----------------------------

print("\nEjemplos originales de DIRECCION:")
print(obras["direccion"].head(20))

obras["direccion"] = obras["direccion"].astype(str).str.strip().str.lower()
obras["direccion"] = obras["direccion"].str.replace(r"\s+", " ", regex=True)
obras["direccion"] = obras["direccion"].replace(["", " "], pd.NA)


""" abreviaturasVariantes = {
    "av.": "avenida",
    "av ": "avenida ",
    "dr.": "doctor",
    "pte.": "presidente",
    "cnl.": "coronel",
    "gral.": "general",
    "prof.": "profesor",
    "pte ": "presidente ",
    "cnel.": "coronel",
    "s/n": "sin numero",
}

for abrev, completo in abreviaturasVariantes.items():
    obras["direccion"] = obras["direccion"].str.replace(abrev, completo, regex=False) """

print("\nColumna DIRECCION limpia:")
print(obras["direccion"].head(20))


#--------------------------- Limpieza de las columnas LAT y LNG ----------------------------

print("\nEjemplos originales de LAT y LNG:")
print(obras["lat"].head(20))
print(obras["lng"].head(20))

for col in ["lat", "lng"]:
    obras[col] = obras[col].astype(str).str.strip()
    obras[col] = obras[col].replace(["", " "], pd.NA)
    obras[col] = obras[col].str.replace(",", ".", regex=False)
    obras[col] = pd.to_numeric(obras[col], errors='coerce')


print("\nColumnas LAT y LNG limpias:")
print(obras["lat"].head(20))
print(obras["lng"].head(20))

#--------------------------- Limpieza de columnas Chardfield ----------------------------

# Lista de columnas a limpiar
cols = [
    "entorno", "nombre", "etapa", "tipo", "area_responsable", "descripcion", "barrio", "direccion", 
    "imagen_1", "licitacion_oferta_empresa", "contratacion_tipo", "nro_contratacion", "cuit_contratista",
    "expediente-numero", "financiamiento"
]

# Limpieza
for col in cols:
    if col in obras.columns:
        obras[col] = obras[col].astype(str).str.strip()
        obras[col] = obras[col].replace(["", "nan", " "], pd.NA)
        obras[col] = obras[col].apply(lambda x: unidecode(x) if pd.notna(x) else x)

# Tratamiento especial para columnas con separadores
for col in ["cuit_contratista", "expediente-numero"]:
    if col in obras.columns:
        obras[col] = obras[col].str.replace(r"\s*;\s*", ";", regex=True)


# Eliminar registro con caracteres raros en expediente-numero
if "expediente-numero" in obras.columns:
    obras = obras[~obras["expediente-numero"].str.contains("EX-2016- 25.688.941í¢ÂÂMGEYA-DGIURB", na=False)]


# Mostrar resultados
for col in cols:
    if col in obras.columns:
        print(f"\nColumna {col.upper()} limpia:")
        print(obras[col].head(20))


# Se guarda el DataFrame limpio en un nuevo archivo CSV
obras.to_csv("observatorioObrasUrbanas_limpio.csv", index=False, na_rep="")