from abc import ABC, abstractmethod
from modelo_orm2 import db, Obra, Entorno, Etapa, TipoObra, ContratacionTipo, AreaResponsable, Barrio, Comuna, Contratista, Direccion

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from unidecode import unidecode

class GestionarObra(ABC):

    @classmethod
    def connect_db(cls):
        try:
            db.connect()
        except Exception as e:
            print('\t[ERROR] - conectando DB\n', e)

    @classmethod
    def extraer_datos(cls):
        try:
            dataframe_crudo = pd.read_csv('observatorio-de-obras-urbanas.csv', sep=';', encoding='latin1')
        except Exception as e:
            print('\t[ERROR] - extraer_datos fallo')
        return dataframe_crudo 

    @classmethod
    def limpiar_datos(cls):

        obras = cls.extraer_datos()
        #Eliminar columnas "UNNAMED" al final del archivo
        obras = obras.loc[:, ~obras.columns.str.startswith("Unnamed")]

        #Eliminar columnas que no se necesitan para el análisis.
        #Estas columnas no aportan información relevante para el análisis de obras urbanas.

        columnas_a_eliminar = [
            "imagen_2", "imagen_3", "imagen_4",
            "beneficiarios", "mano_obra", "compromiso", "destacada",
            "ba_elige", "link_interno", "pliego_descarga", "estudio_ambiental_descarga",
            "financiamiento"
        ]
        obras.drop(columns=columnas_a_eliminar, inplace=True, errors="ignore")

        #--------------------------- Limpieza de renglones repetidos ------------------

        duplicados = obras[obras.duplicated(keep=False)]

        # Eliminar filas duplicadas, conservando solo la primera aparición
        obras = obras.drop_duplicates(keep='first')

        #--------------------------- Limpieza de acentos  ----------------------------

        
        # jon agrega eliminar acentos en columna "etapa"
        obras['etapa'] = obras['etapa'].astype(str).apply(unidecode)

        # Eliminar acentos en la columna "entorno"
        obras["entorno"] = obras["entorno"].astype(str).apply(unidecode)

        # Eliminar acentos en la columna "nombre"
        obras["nombre"] = obras["nombre"].astype(str).apply(unidecode)

        # Eliminar acentos en la columna "tipo"
        obras["tipo"] = obras["tipo"].astype(str).apply(unidecode)

        # Eliminar acentos en la columna "area_responsable"
        obras["area_responsable"] = obras["area_responsable"].astype(str).apply(unidecode)

        # Eliminar acentos en la columna "descripcion"
        obras["descripcion"] = obras["descripcion"].astype(str).apply(unidecode)

        #--------------------------- Unificar formato para columna "MONTO_CONTRATO" ----------------------------
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

        # --------------------------- Limpieza y formateo de TODAS las columnas que contienen "fecha" ----------------------------

        obras["fecha_inicio"] = obras["fecha_inicio"].replace(
            ["", "A/D", "a/d", "s/d", "S/D", "Sin dato", "SIN DATO", None], pd.NaT
        )
        
        obras['lat'] = obras['lat'].replace(["", 'N/A', None], pd.NaT)
        obras['lng'] = obras['lng'].replace(["", 'N/A', None], pd.NaT)
        obras['imagen_1'] = obras['imagen_1'].replace(["", 'N/A', None], pd.NaT)

        obras["fecha_inicio"] = pd.to_datetime(obras["fecha_inicio"], errors="coerce")

        #Columna "FECHA_FIN_INICIAL"
        obras["fecha_fin_inicial"] = obras["fecha_fin_inicial"].replace(
            ["", "A/D", "a/d", "s/d", "S/D", "Sin dato", "SIN DATO", None], pd.NaT
        )

        obras["fecha_fin_inicial"] = pd.to_datetime(obras["fecha_fin_inicial"], errors="coerce")

        #--------------------------- Limpieza de columna PLAZO_MESES ----------------------------

        # Limpiar la columna "plazo_meses" y dejar solo enteros
        obras["plazo_meses"] = obras["plazo_meses"].replace(
            ["", "A/D", "a/d", "s/d", "S/D", "Sin dato", "SIN DATO", None], pd.NA
        )
        obras["plazo_meses"] = pd.to_numeric(obras["plazo_meses"], errors="coerce")
        obras["plazo_meses"] = np.ceil(obras["plazo_meses"].fillna(0)).astype(int)


        #--------------------------- Limpieza de columna COMUNA ----------------------------

        obras["comuna"] = obras["comuna"].replace(["", " "], pd.NA)

        #--------------------------- Limpieza de columna BARRIO ----------------------------

        obras["barrio"] = obras["barrio"].astype(str).str.strip().str.lower()
        obras["barrio"] = obras["barrio"].str.replace(r"\s+", " ", regex=True)
        obras["barrio"] = obras["barrio"].replace(["", " "], pd.NA)
        obras["barrio"] = obras["barrio"].astype(str).apply(unidecode)


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

        #--------------------------- Limpieza de columna DIRECCION ----------------------------

        obras["direccion"] = obras["direccion"].astype(str).str.strip().str.lower()
        obras["direccion"] = obras["direccion"].str.replace(r"\s+", " ", regex=True)
        obras["direccion"] = obras["direccion"].replace(["", " "], pd.NA)
        obras["direccion"] = obras["direccion"].astype(str).apply(unidecode)


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

        #--------------------------- Limpieza de columna PORCENTAJE_AVANCE ----------------------------

        # Reemplazar espacios en blanco por 0
        #obras["porcentaje_avance"] = obras["porcentaje_avance"].replace(["", " "], "0")

        # Reemplazar espacios en blanco por nulos 
        obras["porcentaje_avance"] = obras["porcentaje_avance"].replace(["", " "], pd.NA)

        # Eliminar símbolos como "%" y convertir a número entero
        obras["porcentaje_avance"] = obras["porcentaje_avance"].astype(str).str.replace("%", "", regex=False)
        obras["porcentaje_avance"] = pd.to_numeric(obras["porcentaje_avance"], errors="coerce").fillna(0).astype(int)

        #--------------------------- Limpieza de columna LICITACION_OFERTA_EMPRESA ----------------------------

        # Reemplazar espacios vacíos por nulos 
        obras["licitacion_oferta_empresa"] = obras["licitacion_oferta_empresa"].astype(str).str.strip()
        obras["licitacion_oferta_empresa"] = obras["licitacion_oferta_empresa"].str.replace(r"\s+", "", regex=True)
        obras["licitacion_oferta_empresa"] = obras["licitacion_oferta_empresa"].replace(["", " "], pd.NA)

        #--------------------------- Limpieza de columna LICITACION_ANIO ----------------------------

        # Reemplazar espacios vacíos por nulos 
        obras["licitacion_anio"] = obras["licitacion_anio"].astype(str).str.strip()
        obras["licitacion_anio"] = obras["licitacion_anio"].str.replace(r"\s+", "", regex=True)
        obras["licitacion_anio"] = obras["licitacion_anio"].replace(["", " "], pd.NA)

        #--------------------------- Limpieza de columna CONTRATACION_TIPO ----------------------------

        # Reemplazar espacios vacíos por nulos 
        obras["contratacion_tipo"] = obras["contratacion_tipo"].replace(["", " "], pd.NA)

        # Eliminar acentos en la columna "contratacion_tipo"
        obras["contratacion_tipo"] = obras["contratacion_tipo"].astype(str).apply(unidecode)


        #--------------------------- Limpieza de columna NRO_CONTRATACION ----------------------------

        # Reemplazar espacios vacíos por nulos
        obras["nro_contratacion"] = obras["nro_contratacion"].astype(str).str.strip()
        obras["nro_contratacion"] = obras["nro_contratacion"].str.replace(r"\s+", "", regex=True)
        obras["nro_contratacion"] = obras["nro_contratacion"].replace(["", " "], pd.NA)

        #--------------------------- Limpieza de columna CUIT_CONTRATISTA----------------------------

        # Reemplazar espacios vacíos por nulos 
        obras["cuit_contratista"] = obras["cuit_contratista"].astype(str).str.strip()
        obras["cuit_contratista"] = obras["cuit_contratista"].str.replace(r"\s*;\s*", ";", regex=True)  # quita espacios antes/después de ;
        obras["cuit_contratista"] = obras["cuit_contratista"].replace(["", " "], pd.NA)


        #--------------------------- Limpieza de columna EXPEDIENTE-NUMERO ----------------------------

        # Reemplazar espacios vacíos por nulos 
        obras["expediente-numero"] = obras["expediente-numero"].astype(str).str.strip()
        obras["expediente-numero"] = obras["expediente-numero"].str.replace(r"\s*;\s*", ";", regex=True)  # quita espacios antes/después de ;
        obras["expediente-numero"] = obras["expediente-numero"].replace(["", " "], pd.NA)

        # Eliminar el registro con caracteres raros
        obras = obras[~obras["expediente-numero"].str.contains("EX-2016- 25.688.941í¢ÂÂMGEYA-DGIURB", na=False)]
        # Se guarda el DataFrame limpio en un nuevo archivo CSV
        obras.to_csv("observatorioObrasUrbanas_limpio.csv", index=False, encoding="utf-8")
        return True


    @classmethod
    def mapear_orm(cls):
        try:
        # Mensaje para saber que estamos en este paso
            print("[DEBUG] - Mapeando la base de datos...")

            # La línea clave: le pasamos una lista con TODAS nuestras clases de modelo
            db.create_tables([
                Entorno,
                Etapa,
                TipoObra,
                ContratacionTipo,
                AreaResponsable,
                Barrio,
                Comuna,
                Contratista,
                Direccion,
                Obra  # La tabla principal al final, por buena costumbre
            ])
        except Exception as e:
            print('[ERROR] - mapear_orm -', e)
        
    @classmethod
    def cargar_datos(cls):
        cls.limpiar_datos()
        datos_limpios = pd.read_csv('observatorioObrasUrbanas_limpio.csv', encoding='latin1')
        return datos_limpios 

@classmethod
def nueva_obra(cls):
    
    #Crear una nueva instancia de Obra pidiendo los datos por input, validando claves foráneas, guardando en la DB con save() y retornando la instancia creada.
   
    from modelo_orm2 import (
        Obra, Etapa, TipoObra, ContratacionTipo,
        AreaResponsable, Barrio, Direccion, Contratista
    )
    print("=== Crear nueva Obra ===")

    # Función interna para buscar y validar claves foráneas
    def elegir_instancia(modelo, campo="nombre"):
        while True:
            valor = input(f"Ingrese {campo} para {modelo.__name__}: ").strip()
            try:
                instancia = modelo.get(getattr(modelo, campo) == valor)
                return instancia
            except modelo.DoesNotExist:
                print(f"No existe {modelo.__name__} con {campo} '{valor}'. Intente nuevamente.")

    # Selección de claves foráneas
    etapa = elegir_instancia(Etapa)
    tipo = elegir_instancia(TipoObra)
    contratacion_tipo = elegir_instancia(ContratacionTipo)
    area_responsable = elegir_instancia(AreaResponsable)
    barrio = elegir_instancia(Barrio)
    ubicacion = input("Ingrese ubicación/dirección de la obra: ").strip()
    direccion, _ = Direccion.get_or_create(ubicacion=ubicacion, barrio=barrio)

    # Datos simples de la obra
    nombre = input("Nombre de la obra: ").strip()
    descripcion = input("Descripción: ").strip()

    while True:
        try:
            monto_contrato = float(input("Monto del contrato: ").replace(",", "."))
            break
        except ValueError:
            print("Monto inválido. Ingrese un número (use punto o coma para decimales).")

    while True:
        fecha_inicio = input("Fecha de inicio (YYYY-MM-DD): ").strip()
        if fecha_inicio == "" or len(fecha_inicio.split("-")) == 3:
            break
        print("Fecha inválida. Formato esperado: YYYY-MM-DD o dejar vacío.")

    while True:
        try:
            porcentaje_avance = float(input("Porcentaje de avance (0-100): ").replace(",", "."))
            break
        except ValueError:
            print("Porcentaje inválido. Ingrese un número (use punto o coma para decimales).")

    while True:
        fecha_fin_inicial = input("Fecha fin inicial (YYYY-MM-DD): ").strip()
        if fecha_fin_inicial == "" or len(fecha_fin_inicial.split("-")) == 3:
            break
        print("Fecha inválida. Formato esperado: YYYY-MM-DD o dejar vacío.")

    while True:
        try:
            plazo_meses = int(input("Plazo en meses: "))
            break
        except ValueError:
            print("Valor inválido. Ingrese un número entero.")

    contratista = elegir_instancia(Contratista, campo="nombre_empresa")

    while True:
        try:
            licitacion_anio = int(input("Año de licitación: "))
            break
        except ValueError:
            print("Año inválido. Ingrese un número entero.")

    imagen_1 = input("Ruta imagen (opcional): ").strip() or None

    while True:
        try:
            mano_obra = int(input("Mano de obra (cantidad de personas): "))
            break
        except ValueError:
            print("Valor inválido. Ingrese un número entero.")

    # Crear la instancia de Obra (aún no guardada)
    obra = Obra(
        etapa=etapa,
        tipo=tipo,
        contratacion_tipo=contratacion_tipo,
        area_responsable=area_responsable,
        direccion=direccion,
        nombre=nombre,
        descripcion=descripcion,
        monto_contrato=monto_contrato,
        fecha_inicio=fecha_inicio if fecha_inicio else None,
        porcentaje_avance=porcentaje_avance,
        fecha_fin_inicial=fecha_fin_inicial if fecha_fin_inicial else None,
        plazo_meses=plazo_meses,
        licitacion_oferta_empresa=contratista,
        licitacion_anio=licitacion_anio,
        imagen_1=imagen_1,
        mano__obra=mano_obra
    )

    try:
        obra.save()  # Persistencia en la base de datos
        print("Obra creada exitosamente.")
        return obra
    except Exception as e:
        print("Error al crear la obra:", e)
        return None

# ACLARACION ENORME: El punto 17 esta fuertemente relacionado con el 4f asi que ya estaria casi resuelto por este lado.
# Habria que chequear a la larga si no hay que añadirle cosas en base a los siguientes ejercicios

@classmethod
def obtener_indicadores(cls):
    print("Listado de todas las áreas responsables:")
    for area in AreaResponsable.select():
        print("-", area.nombre)

    print("Listado de todos los tipos de obra:")
    for tipo in TipoObra.select():
        print("-", area.nombre)

    print("Cantidad de obras por etapa:")
    from peewee import fn
    query_etapas = (Obra
        .select(Etapa.nombre, fn.COUNT(Obra.id).alias('cantidad'))
        .join(Etapa)
        .group_by(Etapa)
        )
    for row in query_etapas:
        print(f"- {row.etapa.nombre}: {row.cantidad}")

        
    print("Obras y monto total por tipo de obra:")
    query_tipo = (Obra
        .select(TipoObra.nombre, fn.COUNT(Obra.id).alias('cantidad'), fn.SUM(Obra.monto_contrato).alias('monto_total'))
        .join(TipoObra)
        .group_by(TipoObra)
        )
    for row in query_tipo:
        print(f"- {row.tipo.nombre}: {row.cantidad} obras, ${row.monto_total:,.2f}")

     
    print("Barrios en comunas 1, 2 y 3:")
    comunas = Comuna.select().where(Comuna.nombre.in_(["1", "2", "3"]))
    barrios = Barrio.select().where(Barrio.comuna.in_(comunas))
    for barrio in barrios:
        print(f"- {barrio.nombre} (Comuna {barrio.comuna.nombre})")

    # Busca la etapa cuyo nombre contenga "Finalizada" y cuenta cuántas obras tienen esa etapa con un plazo menor o igual a 24 meses.
    print("\nCantidad de obras finalizadas en plazo ≤ 24 meses:")
    try:
        etapa_finalizada = Etapa.get(Etapa.nombre.contains("Finalizada"))
        obras_finalizadas = Obra.select().where(
        (Obra.etapa == etapa_finalizada) & (Obra.plazo_meses <= 24)
        ).count()
        print(f"{obras_finalizadas} obras")
    except Etapa.DoesNotExist:
        print("No se encontró etapa 'Finalizada'.")

       # Suma de todos los montos de contrato de las obras registradas y muestra el resultado.
        print("Monto total de inversión:")
        total = Obra.select(fn.SUM(Obra.monto_contrato)).scalar()
        print(f"${total:,.2f}" if total else "$0.00")

        

if __name__ == '__main__':
    print('\t[DEBUG] - conectando DB')
    GestionarObra.connect_db()
    print('\t[DEBUG] - extrayendo datos (main)')
    GestionarObra.extraer_datos()
    print('\t[DEBUG] - cargando datos')
    GestionarObra.cargar_datos()
    print('\t[DEBUG] - mapeando a la DB')
    GestionarObra.mapear_orm()
    print('\t[DEBUG] - creando nueva obra')
    GestionarObra.nueva_obra()

