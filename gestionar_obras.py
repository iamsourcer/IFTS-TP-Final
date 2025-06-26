from abc import ABC, abstractmethod
from modelo_orm import *

from datetime import datetime, date
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

        #eliminación de acentos en las columnas de texto
        for col in obras.columns:
            if col in ["entorno", "nombre", "etapa", "tipo", "area_responsable", "descripcion", "barrio", "direccion", "licitacion_oferta_empresa", 
                        "contratacion_tipo", "nro_contratacion", "cuit_contratista", "expediente_numero", "financiamiento"]:
                obras[col] = obras[col].astype(str).apply(unidecode)

        #----------------------------------------- Eliminación de Columnas -----------------------------------------
        #Eliminar columnas "UNNAMED" al final del archivo
        obras = obras.loc[:, ~obras.columns.str.startswith("Unnamed")]

        #Eliminar columnas que no se necesitan para el análisis.
        #Estas columnas no aportan información relevante para el análisis de obras urbanas.
        columnas_a_eliminar = [
                    "imagen_2", "imagen_3", "imagen_4", "beneficiarios", "compromiso", "ba_elige", "link_interno", "pliego_descarga", "estudio_ambiental_descarga"
                ]
        obras.drop(columns=columnas_a_eliminar, inplace=True, errors="ignore")

        #--------------------------- Limpieza de renglones repetidos ------------------

        duplicados = obras[obras.duplicated(keep=False)]
        print(duplicados)

        # Eliminar filas duplicadas, conservando solo la primera aparición
        obras = obras.drop_duplicates(keep='first')


        #--------------------------- Unificar formato para columna "MONTO_CONTRATO" ----------------------------

        # Convertir a string y eliminar espacios en blanco 
        obras["monto_contrato"] = obras["monto_contrato"].astype(str).str.strip()
        #Elimina simbolo de pesos y espacios
        obras["monto_contrato"] = obras["monto_contrato"].str.replace(r"[\$\s]", "", regex=True)
        # Eliminar solo los puntos de los miles (antes de la coma)
        obras["monto_contrato"] = obras["monto_contrato"].str.replace(".", "", regex=False)
        obras["monto_contrato"] = obras["monto_contrato"].str.replace(",", ".", regex=False)
        obras["monto_contrato"] = obras["monto_contrato"].replace(["", " "], 0)
        obras['monto_contrato'] = obras['monto_contrato'].fillna(0)
        #Convertir a float
        obras["monto_contrato"] = pd.to_numeric(obras["monto_contrato"], errors='coerce')
        #Redondear a 2 decimales
        #obras["monto_contrato"] = obras["monto_contrato"].round(2)

        # --------------------------- Limpieza y formateo de TODAS las columnas que contienen "fecha" ----------------------------

        obras["fecha_inicio"] = pd.to_datetime(obras["fecha_inicio"], errors="coerce")
        obras["fecha_fin_inicial"] = pd.to_datetime(obras["fecha_fin_inicial"], errors="coerce")

        #--------------------------- Limpieza de columna PLAZO_MESES ----------------------------

        # Limpiar la columna "plazo_meses" y dejar solo enteros
        obras["plazo_meses"] = obras["plazo_meses"].replace(
            ["", "A/D", "a/d", "s/d", "S/D", "Sin dato", "SIN DATO", None], 0
        )
        obras["plazo_meses"] = pd.to_numeric(obras["plazo_meses"], errors="coerce")
        obras['plazo_meses'] = obras['plazo_meses'].fillna(0).astype(int)

        #--------------------------- Limpieza de columna PORCENTAJE_AVANCE ----------------------------

        # Reemplazar espacios en blanco por nulos 
        obras["porcentaje_avance"] = obras["porcentaje_avance"].replace(["", " "], 0)

        # Eliminar símbolos como "%" y convertir a número entero
        obras["porcentaje_avance"] = obras["porcentaje_avance"].astype(str).str.replace("%", "", regex=False)
        obras["porcentaje_avance"] = pd.to_numeric(obras["porcentaje_avance"], errors="coerce")
        obras['porcentaje_avance'] = obras['porcentaje_avance'].fillna(0).astype(float)

        #--------------------------- Limpieza de columna LICITACION_ANIO ----------------------------

        # Reemplazar espacios vacíos por nulos 
        obras["licitacion_anio"] = obras["licitacion_anio"].replace(["", " "], 0)
        obras['licitacion_anio'] = obras['licitacion_anio'].fillna(0)
        obras["licitacion_anio"] = pd.to_numeric(obras["licitacion_anio"], errors="coerce")

        #--------------------------- Limpieza de columna MANO_OBRA ----------------------------

        obras["mano_obra"] = obras["mano_obra"].replace(["", " "], 0)
        obras["mano_obra"] = pd.to_numeric(obras["mano_obra"], errors="coerce")
        obras['mano_obra'] = obras['mano_obra'].fillna(0)

        #--------------------------- Limpieza de la columna DESTACADA -------------------------

        obras["destacada"] = obras["destacada"].astype(str).str.strip().str.upper()
        obras["destacada"] = obras["destacada"].apply(lambda x:True if x == "SI" else False)

        #--------------------------- Limpieza de columna COMUNA ----------------------------

        obras["comuna"] = obras["comuna"].replace(["", " "], 0)
        obras["comuna"] = pd.to_numeric(obras["comuna"], errors="coerce")

        comunaVariantes = {
                "4 y 1" : "4",
                "1 a 15" : "1",
                "14, 2 , 1" : "14",
                "1 y 4" : "1",
                "7 y 14" : "7",
                "7, 15 y 14" : "7",
                "7 y 9" : "9",
                "4, 8 y 9" : "8", 
                "7, 8 y 9" : "7",
                "." : "0",
                "8 y 12" : "8",
                "1, 2, 3, 4, 5, 6, 7, 8, 9 y 10" :"1",
                "12 y 13" : "12",
                "10/11/12/13/14/15" : "10"
            }

        obras["comuna"] = obras["comuna"].replace(comunaVariantes)

        #--------------------------- Limpieza de columna BARRIO ----------------------------

        obras["barrio"] = obras["barrio"].astype(str).str.strip().str.lower()
        obras["barrio"] = obras["barrio"].str.replace(r"\s+", " ", regex=True)


        barrioVariantes = {       
            ".": " ",                    #Esto reemplaza las variantes en la columna de barrios, pero hay que revisar uno a uno las diferentes opciones
            "Villa 6 - Barrio Cildañez": "villa 6",
            "NuÃ±ez": "nuñez",
            "Cuenca Matanza- Riachuelo": "cuenca matanza",
            "Barracas y Nueva Pompeya": "barracas",
            "La Boca y San Telmo": "la boca",
            "Territorio CABA": "territorio caba",
            "Recoleta, Palermo y Retiro": "recoleta",
            "San Nicolas, Monserrat, San Telmo y La Boca": "san nicolas",
            "P. Chacabuco/Palermo": "parque chacabuco",
            "P. Chacabuco/Agronomía/ Palermo": "parque chacabuco",
            "Flores, Floresta": "flores",
            "Mataderos, Villa Riachuelo, Barracas, Nueva Pompeya, Villa Lugano y La Boca": "mataderos",
            "Villa Soldati, Flores, Floresta, Parque Avellaneda, Mataderos, Villa Lugano, Villa Riachuelo, Villa Lugano": "villa soldati",
            "Villa Lugano, Parque Avellaneda y Flores": "villa lugano",
            "Villa Soldati y Saavedra": "villa soldati",
            "Villa Soldati, Flores, Floresta, Parque Avellaneda, Mataderos, Villa Lugano, Villa Riachuelo, Villa Lugano, Liniers, Parque Chacabuco, Caballito, Boedo, San Cristobal, Constitución, Boca, Barracas, Parque Patricios  y Nueva Pompeya": "villa soldati",
            "Nuñez y Saavedra": "nuñez",
            "San Nicolas, Monserrat, San Telmo y La Boca": "san nicolas",
            "YERBAL - VILLA LURO - VELEZ SARFIELD FLORESTA - MONTE CASTRO - VILLA DEL PARQUE - VILLA SANTA RITA - PATERNAL - VILLA CRESPO - VILLA URQUIZA": "villa urquiza"

        }
        obras["barrio"] = obras["barrio"].replace(barrioVariantes)

        #--------------------------- Limpieza de columna DIRECCION ----------------------------

        obras["direccion"] = obras["direccion"].astype(str).str.strip().str.lower()
        obras["direccion"] = obras["direccion"].str.replace(r"\s+", " ", regex=True)

        #--------------------------- Limpieza de las columnas LAT y LNG ----------------------------

        for col in ["lat", "lng"]:
            obras[col] = obras[col].astype(str).str.strip()
            obras[col] = obras[col].replace(["", " "], 0)
            obras[col] = obras[col].str.replace(",", ".", regex=False)
            obras[col] = pd.to_numeric(obras[col], errors='coerce')


        # Tratamiento especial para columnas con separadores
        for col in ["cuit_contratista", "expediente-numero"]:
            if col in obras.columns:
                obras[col] = obras[col].str.replace(r"\s*;\s*", ";", regex=True)


        # Eliminar registro con caracteres raros en expediente-numero
        if "expediente-numero" in obras.columns:
            obras = obras[~obras["expediente-numero"].str.contains("EX-2016- 25.688.941í¢ÂÂMGEYA-DGIURB", na=False)]

        
        #--------------------------- Convierte a espacios para que la DB perimita ingresar los datos y que no sean nulos ----------------------------
        campos_char_obligatorios = ["entorno", "nombre", "etapa", "tipo", "area_responsable", "descripcion", "barrio", "direccion", 
                                    "licitacion_oferta_empresa", "contraracion_tipo", "nro_contratacion", "cuit_contratista" 
        ]
        
        for col in campos_char_obligatorios:
            if col in obras.columns:
                obras[col] = obras[col].fillna(" ")


        #Si hay nan o 0, poner valor por defecto
        obras['comuna'] = obras['comuna'].apply(lambda x: int(x) if pd.notna(x) and str(x).lower() != 'nan' else 0)
        obras['barrio'] = obras['barrio'].apply(lambda x: x if pd.notna(x) and str(x).strip().lower() != 'nan' and x.strip() != '' else 'sin barrio')
        obras['nombre'] = obras['nombre'].apply(lambda x: x if pd.notna(x) and str(x).strip().lower() != 'nan' and x.strip() != '' else 'SIN NOMBRE')
        obras['descripcion'] = obras['descripcion'].apply(lambda x: x if pd.notna(x) and str(x).strip().lower() != 'nan' else ' ')
        obras['direccion'] = obras['direccion'].apply(lambda x: x if pd.notna(x) and str(x).strip().lower() != 'nan' else ' ')

        return obras

    @classmethod
    def mapear_orm(cls):

        try:
            cls.connect_db()
            print('\t[DEBUG] - conectando db') 
        except Exception as e:
            print('\t[DEBUG] - Falla al conectar la DB')

        try:
            # Mensaje para saber que estamos en este paso
            print("\t[DEBUG] - Intentando Mapear la base de datos...")

            # La línea clave: le pasamos una lista con TODAS nuestras clases de modelo
            db.create_tables([
                Entorno,
                Etapa,
                TipoObra,
                ContratacionTipo,
                AreaResponsable,
                Comuna, 
                Barrio,
                Contratista,
                Direccion,
                Obra  # La tabla principal al final, por buena costumbre
            ], safe=True)

            db.close()

        except Exception as e:
            print('[ERROR] - mapear_orm -', e)


    @classmethod
    def cargar_datos(cls):

        datos_limpios = cls.limpiar_datos()

        for index, row in datos_limpios.iterrows():
            #Validaciones y valores por defecto
            entorno_name = row['entorno'] if pd.notna(row['entorno']) and str(row['entorno']).strip().lower() != 'nan' else 'SIN ENTORNO'
            etapa_name = row['etapa'] if pd.notna(row['etapa']) and str(row['etapa']).strip().lower() != 'nan' else 'SIN ETAPA'
            tipo_name = row['tipo'] if pd.notna(row['tipo']) and str(row['tipo']).strip().lower() != 'nan' else 'SIN TIPO'
            contratacion_tipo_name = row['contratacion_tipo'] if pd.notna(row['contratacion_tipo']) and str(row['contratacion_tipo']).strip().lower() != 'nan' else 'SIN CONTRATACION'
            area_responsable_name = row['area_responsable'] if pd.notna(row['area_responsable']) and str(row['area_responsable']).strip().lower() != 'nan' else 'SIN AREA'
            comuna_name = row['comuna'] if pd.notna(row['comuna']) and str(row['comuna']).strip().lower() != 'nan' else 0
            barrio_name = row['barrio'] if pd.notna(row['barrio']) and str(row['barrio']).strip().lower() != 'nan' and row['barrio'].strip() != '' else 'sin barrio'
            nombre_obra = row['nombre'] if pd.notna(row['nombre']) and str(row['nombre']).strip().lower() != 'nan' and row['nombre'].strip() != '' else 'SIN NOMBRE'
            descripcion_obra = row['descripcion'] if pd.notna(row['descripcion']) and str(row['descripcion']).strip().lower() != 'nan' else ' '
            direccion_obra = row['direccion'] if pd.notna(row['direccion']) and str(row['direccion']).strip().lower() != 'nan' else ' '
            

            entorno, _ = Entorno.get_or_create(nombre=entorno_name)
            etapa, _ = Etapa.get_or_create(nombre=etapa_name)
            tipo, _ = TipoObra.get_or_create(nombre=tipo_name)
            contratacion_tipo, _ = ContratacionTipo.get_or_create(nombre=contratacion_tipo_name)
            area_responsable, _ = AreaResponsable.get_or_create(nombre=area_responsable_name)
            comuna, _ = Comuna.get_or_create(nombre=comuna_name)

            # --- ADD THESE DEBUG PRINTS ---
            print(f"DEBUG: Processing Comuna: '{comuna_name}'. Object: {comuna} (ID: {getattr(comuna, 'id', None)})")
            if comuna is None or not hasattr(comuna, 'id') or comuna.id is None:
                raise ValueError(f"Comuna object is invalid before creating Barrio: {comuna_name}")
            # --- END DEBUG PRINTS ---

            barrio, _ = Barrio.get_or_create(nombre=row['barrio'], comuna=comuna)

            contratista, _ = Contratista.get_or_create(
                    nombre_empresa=row['licitacion_oferta_empresa'],
                    cuit_contratista=row['cuit_contratista'],
                    nro_contratacion=row['nro_contratacion'],
                    expediente_numero=row['expediente-numero'])
             
            # --- MODIFIED DIRECCION HANDLING ---
            lat_val = row['lat']
            lng_val = row['lng']

            # Convert pandas NaN to None, or handle other non-numeric strings
            if pd.isna(lat_val): # Check for pandas NaN
                lat_val = None
            elif not isinstance(lat_val, (int, float)): # If it's not a number, try converting
                try:
                    lat_val = float(lat_val)
                except (ValueError, TypeError):
                    lat_val = None # Set to None if conversion fails

            if pd.isna(lng_val): # Check for pandas NaN
                lng_val = None
            elif not isinstance(lng_val, (int, float)):
                try:
                    lng_val = float(lng_val)
                except (ValueError, TypeError):
                    lng_val = None # Set to None if conversion fails

            direccion, _ = Direccion.get_or_create(ubicacion=row['direccion'],
                                                barrio=barrio,
                                                lat=lat_val,
                                                lng=lng_val)
            
            mano_obra = row['mano_obra']
            if pd.isna(mano_obra):
                mano_obra = 0

            monto_contrato = row['monto_contrato']
            if pd.isna(monto_contrato):
                monto_contrato = 0

            licitacion_anio = row['licitacion_anio']
            if pd.isna(licitacion_anio):
                licitacion_anio = 0

            fecha_inicio = row['fecha_inicio']
            if pd.isna(fecha_inicio):
                fecha_inicio = None

            fecha_fin_inicial = row['fecha_fin_inicial']
            if pd.isna(fecha_fin_inicial):
                fecha_fin_inicial = None

            try:
                obra = Obra(
                    entorno=entorno,
                    etapa=etapa,
                    tipo=tipo,
                    contratacion_tipo=contratacion_tipo, 
                    area_responsable=area_responsable,
                    direccion=direccion, 
                    licitacion_oferta_empresa=contratista, 
                    nombre=nombre_obra,
                    descripcion=descripcion_obra,
                    monto_contrato=monto_contrato,
                    fecha_inicio=fecha_inicio,
                    fecha_fin_inicial=fecha_fin_inicial,
                    plazo_meses=row['plazo_meses'],
                    porcentaje_avance=row['porcentaje_avance'],
                    licitacion_anio=licitacion_anio,
                    imagen_1=row['imagen_1'],
                    mano_obra=mano_obra,
                    destacada=row['destacada'],
                    financiamiento=row['financiamiento'])
                obra.save()
            except Exception as e:
                print(f'[ERROR] - Error al grabar en db - {e}')

        db.close()


    @classmethod
    def nueva_obra(cls):
        try:
            #Entorno
            while True:
                nombre_entorno = input("Ingrese el Entorno para la Obra: ").strip()
                entorno = Entorno.get_or_none(nombre=nombre_entorno)
                if entorno:
                    break
                print("Entorno no encontrado. Intente nuevamente.")
            #Etapa
            while True:
                nombre_etapa = input("Ingrese la Etapa: ").strip()
                etapa = Etapa.get_or_none(nombre=nombre_etapa)
                if etapa:
                    break
                print("Etapa no encontrada. Intente nuevamente.")
            #Tipo de Obra
            while True:
                nombre_tipo_obra = input("Ingrese el Tipo de Obra: ").strip()
                tipo = TipoObra.get_or_none(nombre=nombre_tipo_obra)
                if tipo:
                    break
                print("Tipo de Obra no encontrado. Intente nuevamente.")
            #Tipo de Contratación
            while True:
                nombre_tipo_contratacion = input("Ingrese el Tipo de Contratación: ").strip()
                contratacion_tipo = ContratacionTipo.get_or_none(nombre=nombre_tipo_contratacion)
                if contratacion_tipo:
                    break
                print("Tipo de Contratación no encontrado. Intente nuevamente.")
            #Area Responsable
            while True:
                nombre_area_responsable = input("Ingrese el Área Responsable: ").strip()
                area_responsable = AreaResponsable.get_or_none(nombre=nombre_area_responsable)
                if area_responsable:
                    break
                print("Area responsable no encontrada. Intente nuevamente.")
            #Comuna
            while True:
                nombre_comuna = input("Ingrese el número de la Comuna: ").strip()
                comuna = Comuna.get_or_none(nombre=nombre_comuna)
                if comuna:
                    break
                print("Comuna no encontrada. Intente nuevamente.")

            barrios_validos = [barrio.nombre for barrio in Barrio.select().where(Barrio.comuna == comuna)]
            if barrios_validos:
                print(f"Barrios válidos para la comuna {comuna.nombre}:")
                for barrios in barrios_validos:
                    print(f" - {barrios}")
            else:
                print(f"No hay barrios registrados para la comuna {comuna.nombre}.")

            #Barrio
            while True:
                nombre_barrio = input("Ingrese el nombre del barrio: ").strip()
                barrio = Barrio.get_or_none(nombre=nombre_barrio, comuna=comuna)
                if barrio:
                    break
                print("Barrio no encontrado para esa Comuna. Intente nuevamente.")
            #Direccion
            direccion_ubicacion = input("Ingrese la dirección de la Obra: ").strip()
            direccion_latitud= input("Ingrese la latitud (opcional): ").strip()
            direccion_longitud = input("Ingrese la longitud (opcional): ").strip()
            direccion_latitud = float(direccion_latitud) if direccion_latitud else None
            direccion_longitud = float(direccion_longitud) if direccion_longitud else None
            nueva_direccion, _ = Direccion.get_or_create(
                ubicacion=direccion_ubicacion,
                barrio=barrio,
                lat=direccion_latitud,
                lng=direccion_longitud
            )
            #licitacion_oferta_empresa
            while True:
                nuevo_nombre_empresa = input("Ingrese el nombre de la Empresa Contratista: ").strip()
                nro_cuit_contratista = input("Ingrese el CUIT de la Empresa Contratista: ").strip()
                nueva_empresa_contratista = Contratista.get_or_none(nombre_empresa=nuevo_nombre_empresa, cuit_contratista=nro_cuit_contratista)
                if nueva_empresa_contratista:
                    break
                print("Empresa Contratista no encontrada con ese Nombre y CUIT. Intente nuevamente.")

                nuevo_nro_contratacion = input("Ingrese el número de Contratación de la Empresa (opcioanl): ").strip()
                nuevo_expediente_numero = input("Ingrese el número del Expediente (opcional): ").strip()
                if nuevo_nro_contratacion:
                    nueva_empresa_contratista.nro_contratacion = nuevo_nro_contratacion
                if nuevo_expediente_numero:
                    nueva_empresa_contratista.expediente_numero = nuevo_expediente_numero
                nueva_empresa_contratista.save()
            
            nombre = input("Ingrese el nombre de la Obra: ").strip()
            descripcion = input("Ingrese la descripción de la Obra: ").strip()

            while True:
                try:
                    monto_contrato = float(input("Ingrese el monto del contrato: "))
                    break
                except ValueError:
                    print("El monto debe ser un número válido.")
            
            while True:
                fecha_inicio = input("Ingrese la fecha de inicio (YYYY-MM-DD): ").strip()
                try:
                    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                    break
                except ValueError:
                    print("Formato de fecha incorrecto. Use YYYY-MM-DD.")

            while True:
                fecha_fin_inicial = input("Ingrese la fecha de finalización (YYYY-MM-DD): ").strip()
                try:
                    fecha_fin_inicial = datetime.strptime(fecha_fin_inicial, "%Y-%m-%d").date()
                    break
                except ValueError:
                    print("Formato de fecha incorrecto. Use YYYY-MM-DD.")

            while True:
                try:
                    plazo_meses = int(input("Ingrese el plazo en meses: "))
                    if plazo_meses > 0:
                        break
                    else:
                        print("El plazo debe ser un número mayor a cero.")
                except ValueError:
                    print("El plazo debe ser un número entero.")

            while True:
                try:
                    porcentaje_avance = float(input("Ingrese el porcentaje de avance (0-100): "))
                    if 0 <= porcentaje_avance <= 100:
                        break
                    else:
                        print("El porcentaje debe estar entre 0 y 100.")
                except ValueError:
                    print("El porcentaje debe ser un número.")
            
            while True:
                try:
                    licitacion_anio = int(input("Ingrese el año de licitación: "))
                    break
                except ValueError:
                    print("El año de licitación debe ser un número.")

            imagen = input("Ingrese la URL de la imagen principal (opcional): ").strip()

            while True:
                try:
                    mano_obra = int(input("Ingrese la cantidad de mano de obra: "))
                    break
                except ValueError:
                    print("La mano de obra debe ser un número entero.")

            esta_destacada = input("¿La obra es destacada? (s/n): ").strip().lower() == 's'
            financiamiento = input("Ingrese la fuente de financiamiento: ").strip()

            #Creación de la nueva instancia de Obra 
            
            nueva_obra = Obra(
                entorno = entorno,
                etapa = etapa,
                tipo = tipo,
                contratacion_tipo = contratacion_tipo,
                area_responsable = area_responsable,
                direccion = nueva_direccion,
                licitacion_oferta_empresa = nueva_empresa_contratista,
                nombre = nombre,
                descripcion = descripcion,
                monto_contrato = monto_contrato,
                fecha_inicio = fecha_inicio,
                fecha_fin_inicial = fecha_fin_inicial,
                plazo_meses = plazo_meses,
                porcentaje_avance = porcentaje_avance,
                licitacion_anio = licitacion_anio,
                imagen_1 = imagen,
                mano_obra = mano_obra,
                destacada = esta_destacada,
                financiamiento = financiamiento
            )
            nueva_obra.save()
            print(f"Obra '{nueva_obra.nombre}' creada exitosamente.")
            return nueva_obra

        except Exception as e:
            print(f"[ERROR] - No se pudo crear la nueva Obra: {e}")
            return None


    @classmethod
    def obtener_indicadores(cls):
        print("\n ----------------- INDICADORES DE OBRAS URBANAS ----------------- \n")
        try:
            #a. Listado de todas las áreas responsables.
            print("a. Áreas Responsables: ")
            for area in AreaResponsable.select():
                print(f" - {area.nombre}")

            #b. Listado de todos los tipos de obra.
            print("\n b. Tipos de Obra: ")
            for tipo in TipoObra.select():
                print(f" - {tipo.nombre}")
            
            #c. Cantidad de obras que se encuentran en cada etapa.
            print("\n c. Cantidad de Obras por Etapa: ")
            query_etapas = (Obra
                            .select(Etapa.nombre, fn.COUNT(Obra.id).alias('cantidad'))
                            .join(Etapa)
                            .group_by(TipoObra))
            for row in query_etapas:
                print(f" - {row.etapa.nombre} : {row.cantidad}")

            #d. Cantidad de obras y monto total de inversión por tipo de obra.
            print("\n d. Cantidad de Obras y Monto Total de Inversión por Tipo de Obra: ")
            query_tipo_obra_monto = (Obra
                                     .select(TipoObra.nombre, fn.COUNT(Obra.id).alias('cantidad'), fn.SUM(Obra.monto_contrato).alias('total'))
                                     .join(TipoObra)
                                     .group_by(TipoObra))
            for row in query_tipo_obra_monto:
                print(f" - {row.tipo.nombre} : {row.cantidad} obras, ${row.total:,.2f} de inversión")


            #e. Listado de todos los barrios pertenecientes a las comunas 1, 2 y 3.
            print("\n e. Barrios de las Comunas 1, 2 y 3: ")
            query_barrios = (Barrio
                             .select()
                             .join(Comuna)
                             .where(Comuna.nombre.in_(['1', '2', '3'])))
            for barrio in query_barrios:
                print(f" - {barrio.nombre} (Comuna {barrio.comuna.nombre})")


            #f. Cantidad de obras finalizadas en un plazo menor o igual a 24 meses.
            print("\n f. Obras Finalizadas en un Plazo menor o igual a 24 Meses: ")
            etapa_finalizada = Etapa.get_or_none(nombre="Finalizada")
            if etapa_finalizada:
                obras_finalizadas = Obra.select().where((Obra.etapa == etapa_finalizada) & (Obra.plazo_meses <= 24))
                print(f" - Cantidad: {obras_finalizadas.COUNT()}")
            else: 
                print("No hay etapa 'Finalizada' registrada.")

            #g. Monto total de inversión.
            print("\n g. Monto Total de Inversión: ")
            total_inversion = Obra.select(fn.SUM(Obra.monto_contrato)).scalar() or 0
            print(f" - ${total_inversion:z,.2f}")

        except Exception as e:
            print(f"[Error] - al obtener los indicadores: {e}")


    @classmethod                                #Agrego un método para desconectar la base de datos
    def desconectar_db(cls):
        try:
            db.close()
        except Exception as e:
            print('\t[ERROR] - desconectando DB\n', e)


if __name__ == '__main__':
    """ print('\t[DEBUG] - conectando DB')
    GestionarObra.connect_db()
    print('\t[DEBUG] - extrayendo datos (main)')
    GestionarObra.extraer_datos()
    print('\t[DEBUG] - mapeando a la DB')
    GestionarObra.mapear_orm()
    print('\t[DEBUG] - cargando datos')
    GestionarObra.cargar_datos() """

    #Se crean dos instancias de Obras y se hacen pasar por todos 
    print('\n [INFO] - Creando la Primera Obra.')
    obra1 = GestionarObra.nueva_obra()
    if obra1:
        print('\nAvanzando etapas de la Primera Obra: \n')
        print('\n ------- INICIANDO NUEVO PROYECTO -------')
        obra1.nuevo_proyecto()
        obra1.save()
        print('\n ------- INICIANDO CONTRATACIÓN -------')
        obra1.iniciar_contratacion()
        obra1.save()
        print('\n ------- ADJUDICANDO OBRA -------')
        obra1.adjudicar_obra()
        obra1.save()
        print('\n ------- INICIANDO OBRA -------')
        obra1.iniciar_obra()
        obra1.save()
        print('\n ------- ACTUALIZANDO PORCENTAJE DE AVANCE -------')
        obra1.actualizar_porcentaje_avance()
        obra1.save()
        print('\n ------- INCREMENTANDO PLAZO EN MESES -------')
        obra1.incrementar_plazo()
        obra1.save()
        print('\n ------- INCREMENTANDO MANO DE OBRA -------')
        obra1.incrementar_mano_obra()
        obra1.save()
        while True:
            opcion = input('\n ¿Desea Finalizar o Rescindir la obra? (F / R): ').strip().lower()
            if (opcion == 'f'):
                print('\n ------- FINALIZANDO LA OBRA -------')
                obra1.finalizar_obra()
                obra1.save()
            elif (opcion == 'r'):
                print('\n ------- RESCINDIENDO LA OBRA -------')
                obra1.rescindir_obra()
                obra1.save()
            else:
                print('Debe ingresar una opción válida.')

    
    print('\n [INFO] - Creando la Segunda Obra. \n')
    obra2 = GestionarObra.nueva_obra()
    if obra2:
        print('\nAvanzando etapas de la Primera Obra: ')
        print('\n ------- INICIANDO NUEVO PROYECTO -------')
        obra2.nuevo_proyecto()
        obra2.save()
        print('\n ------- INICIANDO CONTRATACIÓN -------')
        obra2.iniciar_contratacion()
        obra2.save()
        print('\n ------- ADJUDICANDO OBRA -------')
        obra2.adjudicar_obra()
        obra2.save()
        print('\n ------- INICIANDO OBRA -------')
        obra2.iniciar_obra()
        obra2.save()
        print('\n ------- ACTUALIZANDO PORCENTAJE DE AVANCE -------')
        obra2.actualizar_porcentaje_avance()
        obra2.save()
        print('\n ------- INCREMENTANDO PLAZO EN MESES -------')
        obra2.incrementar_plazo()
        obra2.save()
        print('\n ------- INCREMENTANDO MANO DE OBRA -------')
        obra2.incrementar_mano_obra()
        obra2.save()
        while True:
            opcion = input('\n ¿Desea Finalizar o Rescindir la obra? (F / R): ').strip().lower()
            if (opcion == 'f'):
                print('\n ------- FINALIZANDO LA OBRA -------')
                obra2.finalizar_obra()
                obra2.save()
            elif (opcion == 'r'):
                print('\n ------- RESCINDIENDO LA OBRA -------')
                obra2.rescindir_obra()
                obra2.save()
            else:
                print('Debe ingresar una opción válida.')