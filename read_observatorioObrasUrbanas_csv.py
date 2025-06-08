import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from unidecode import unidecode

#Leer el archivo CSV original
obras = pd.read_csv('IFTS-TP-Final/observatorio-de-obras-urbanas.csv', sep=';', encoding='latin1')

#----------------------------------------- Limpieza de datos -----------------------------------------
#Mostrar nombres de columnas y tipos.
print("Columnas")
print(obras.columns)
print("\nTipos de datos:")
print(obras.dtypes)

#----------------------------------------- Eliminación de Columnas -----------------------------------------
#Eliminar columnas "UNNAMED" al final del archivo
obras = obras.loc[:, ~obras.columns.str.startswith("Unnamed")]

print("\nPrimeras filas luego de eliminar columnas innecesarias:")
print(obras.columns)
print(obras.dtypes)

#Eliminar columnas que no se necesitan para el análisis.
#Estas columnas no aportan información relevante para el análisis de obras urbanas.
columnas_a_eliminar = [
    "lat", "lng", "imagen_1", "imagen_2", "imagen_3", "imagen_4",
    "beneficiarios", "mano_obra", "compromiso", "destacada",
    "ba_elige", "link_interno", "pliego_descarga", "estudio_ambiental_descarga",
    "financiamiento"
]
obras.drop(columns=columnas_a_eliminar, inplace=True, errors="ignore")


print("Columnas utiles que quedan:")
print(obras.columns)


#--------------------------- Unificar formato para columna "MONTO_CONTRATO" ----------------------------

print("\nEjemplos originales de monto_contrato:")
print(obras["monto_contrato"].head(10))


#Reemplazar NaN por 0
obras["monto_contrato"] = obras["monto_contrato"].fillna(0)

#quitar simbolos como "$", ".", "," y espacios en blanco
obras["monto_contrato"] = obras["monto_contrato"].astype(str)
obras["monto_contrato"] = obras["monto_contrato"].str.replace("$", "", regex=False)
obras["monto_contrato"] = obras["monto_contrato"].str.strip()

# Eliminar solo los puntos de los miles (antes de la coma)
obras["monto_contrato"] = obras["monto_contrato"].str.replace(".", "", regex=False)

# Reemplazar la coma decimal por punto
obras["monto_contrato"] = obras["monto_contrato"].str.replace(",", ".", regex=False)

#Convertir a float
obras["monto_contrato"] = pd.to_numeric(obras["monto_contrato"], errors='coerce')

# Mostrar los floats sin notación científica y con separador de miles
pd.set_option('display.float_format', '{:,.2f}'.format)

#Redondear a 2 decimales
#obras["monto_contrato"] = obras["monto_contrato"].round(2)

print("\nMonto_contrato ya limpio y como número:")
print(obras["monto_contrato"].head(10))


# --------------------------- Limpieza y formateo de TODAS las columnas que contienen "fecha" ----------------------------

#Columna "FECHA_INICIO"
print(obras["fecha_inicio"].head(10))

obras["fecha_inicio"] = obras["fecha_inicio"].replace(
    ["", "A/D", "a/d", "s/d", "S/D", "Sin dato", "SIN DATO", None], pd.NaT
)

obras["fecha_inicio"] = pd.to_datetime(obras["fecha_inicio"], errors="coerce")
obras["fecha_inicio"] = obras["fecha_inicio"].dt.strftime("%Y-%m-%d")
#obras["fecha_inicio"] = obras["fecha_inicio"].fillna("0000-00-00")
obras["fecha_inicio"] = obras["fecha_inicio"].replace(["", " "], pd.NA)

print("\nfecha_inicio limpia y formateada:")
print(obras["fecha_inicio"].head(650))


#Columna "FECHA_FIN_INICIAL"
print(obras["fecha_fin_inicial"].head(10))

obras["fecha_fin_inicial"] = obras["fecha_fin_inicial"].replace(
    ["", "A/D", "a/d", "s/d", "S/D", "Sin dato", "SIN DATO", None], pd.NaT
)

obras["fecha_fin_inicial"] = pd.to_datetime(obras["fecha_fin_inicial"], errors="coerce")
obras["fecha_fin_inicial"] = obras["fecha_fin_inicial"].dt.strftime("%Y-%m-%d")
#obras["fecha_fin_inicial"] = obras["fecha_fin_inicial"].fillna("0000-00-00")
obras["fecha_fin_inicial"] = obras["fecha_fin_inicial"].replace(["", " "], pd.NA)

print("\nfecha_fin_inicial limpia y formateada:")
print(obras["fecha_fin_inicial"].head(650))





#--------------------------- Limpieza de columna PLAZO_MESES ----------------------------

# Limpiar la columna "plazo_meses" y dejar solo enteros
obras["plazo_meses"] = obras["plazo_meses"].replace(
    ["", "A/D", "a/d", "s/d", "S/D", "Sin dato", "SIN DATO", None], pd.NA
)
obras["plazo_meses"] = pd.to_numeric(obras["plazo_meses"], errors="coerce")
obras["plazo_meses"] = np.ceil(obras["plazo_meses"].fillna(0)).astype(int)


print("\nPlazo_meses limpio, redondeado hacia arriba:")
print(obras["plazo_meses"].head(30))


#--------------------------- Limpieza de columna COMUNA ----------------------------

print("\nEjemplos originales de COMUNA:")
print(obras["comuna"].head(30))

#obras["comuna"] = pd.to_numeric(obras["comuna"], errors="coerce").fillna(0).astype(int)
obras["comuna"] = obras["comuna"].replace(["", " "], pd.NA)

print("\nColumna COMUNA limpia:")
print(obras["comuna"].head(30))


#--------------------------- Limpieza de columna BARRIO ----------------------------

print("\nEjemplos originales de BARRIO:")
print(obras["barrio"].head(30))

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
print(obras["comuna"].head(30))


#--------------------------- Limpieza de columna DIRECCION ----------------------------

print("\nEjemplos originales de DIRECCION:")
print(obras["direccion"].head(30))

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

print("\nColumna DIREECION limpia:")
print(obras["direccion"].head(30))



#--------------------------- Limpieza de columna PORCENTAJE_AVANCE ----------------------------

print("\nEjemplos originales de PORCENTAJE_AVANCE:")
print(obras["porcentaje_avance"].head(30))

# Reemplazar espacios en blanco por 0
#obras["porcentaje_avance"] = obras["porcentaje_avance"].replace(["", " "], "0")

# Reemplazar espacios en blanco por nulos 
obras["fecha_inicio"] = obras["fecha_inicio"].replace(["", " "], pd.NA)

# Eliminar símbolos como "%" y convertir a número entero
obras["porcentaje_avance"] = obras["porcentaje_avance"].astype(str).str.replace("%", "", regex=False)
obras["porcentaje_avance"] = pd.to_numeric(obras["porcentaje_avance"], errors="coerce").fillna(0).astype(int)

print("\nColumna PORCENTAJE_AVANCE limpia:")
print(obras["porcentaje_avance"].head(30))


#--------------------------- Limpieza de columna LICITACION_OFERTA_EMPRESA ----------------------------

# Reemplazar espacios vacíos por nulos 
obras["licitacion_oferta_empresa"] = obras["licitacion_oferta_empresa"].replace(["", " "], pd.NA)

print("\nColumna LICITACION_OFERTA_EMPRESA limpia:")
print(obras["licitacion_oferta_empresa"].head(30))


#--------------------------- Limpieza de columna LICITACION_ANIO ----------------------------

# Reemplazar espacios vacíos por nulos 
obras["licitacion_anio"] = obras["licitacion_anio"].replace(["", " "], pd.NA)

print("\nColumna LICITACION_ANIO limpia:")
print(obras["licitacion_anio"].head(30))


#--------------------------- Limpieza de columna CONTRATACION_TIPO ----------------------------

# Reemplazar espacios vacíos por nulos 
obras["contratacion_tipo"] = obras["contratacion_tipo"].replace(["", " "], pd.NA)

# Eliminar acentos en la columna "contratacion_tipo"
obras["contratacion_tipo"] = obras["contratacion_tipo"].astype(str).apply(unidecode)

print("\nColumna CONTRATACION_TIPO limpia:")
print(obras["contratacion_tipo"].head(30))


#--------------------------- Limpieza de columna NRO_CONTRATACION ----------------------------

# Reemplazar espacios vacíos por nulos 
obras["nro_contratacion"] = obras["nro_contratacion"].replace(["", " "], pd.NA)

print("\nColumna NRO_CONTRATACION limpia:")
print(obras["nro_contratacion"].head(30))


#--------------------------- Limpieza de columna CUIT_CONTRATISTA----------------------------

# Reemplazar espacios vacíos por nulos 
obras["cuit_contratista"] = obras["cuit_contratista"].replace(["", " "], pd.NA)

print("\nColumna CUIT_CONTRATISTA limpia:")
print(obras["cuit_contratista"].head(30))



#--------------------------- Limpieza de columna EXPEDIENTE_NUMERO ----------------------------

# Reemplazar espacios vacíos por nulos 
obras["expediente_numero"] = obras["expediente_numero"].replace(["", " "], pd.NA)

print("\nColumna EXPEDIENTE_NUMERO limpia:")
print(obras["expediente_numero"].head(30))




# Se guarda el DataFrame limpio en un nuevo archivo CSV
obras.to_csv("IFTS-TP-Final/observatorioObrasUrbanas_limpio.csv", index=False, encoding="utf-8")