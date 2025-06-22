from abc import ABC, abstractmethod
from modelo_orm import db, Obra, Entorno, Etapa, TipoObra, ContratacionTipo, AreaResponsable, Barrio, Comuna, Contratista, Direccion

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
            ["", "A/D", "a/d", "s/d", "S/D", "Sin dato", "SIN DATO", None], np.nan
        )
        obras["plazo_meses"] = pd.to_numeric(obras["plazo_meses"], errors="coerce")
        obras["plazo_meses"] = np.ceil(obras["plazo_meses"])
        obras["plazo_meses"] = obras["plazo_meses"].astype('Int64') #Permite nulos

        #--------------------------- Limpieza de columna PORCENTAJE_AVANCE ----------------------------

        # Reemplazar espacios en blanco por nulos 
        obras["porcentaje_avance"] = obras["porcentaje_avance"].replace(["", " "], np.nan)

        # Eliminar símbolos como "%" y convertir a número entero
        obras["porcentaje_avance"] = obras["porcentaje_avance"].astype(str).str.replace("%", "", regex=False)
        obras["porcentaje_avance"] = pd.to_numeric(obras["porcentaje_avance"], errors="coerce")

        #--------------------------- Limpieza de columna LICITACION_ANIO ----------------------------

        # Reemplazar espacios vacíos por nulos 
        obras["licitacion_anio"] = obras["licitacion_anio"].replace(["", " "], np.nan)
        obras["licitacion_anio"] = pd.to_numeric(obras["licitacion_anio"], errors="coerce")
        obras["licitacion_anio"] = obras["licitacion_anio"].astype('Int64')

        #--------------------------- Limpieza de columna MANO_OBRA ----------------------------

        obras["mano_obra"] = obras["mano_obra"].replace(["", " "], np.nan)
        obras["mano_obra"] = pd.to_numeric(obras["mano_obra"], errors="coerce")
        obras["mano_obra"] = obras["mano_obra"].astype('Int64')

        #--------------------------- Limpieza de la columna DESTACADA -------------------------

        obras["destacada"] = obras["destacada"].astype(str).str.strip().str.upper()
        obras["destacada"] = obras["destacada"].apply(lambda x:True if x == "SI" else False)

        #--------------------------- Limpieza de columna COMUNA ----------------------------

        obras["comuna"] = obras["comuna"].astype(str).str.strip().replace(["", " "], np.nan)
        obras["comuna"] = pd.to_numeric(obras["comuna"], errors="coerce")
        obras["comuna"] = obras["comuna"].astype('Int64')


        #--------------------------- Limpieza de columna BARRIO ----------------------------

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

        #--------------------------- Limpieza de columna DIRECCION ----------------------------

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

       #--------------------------- Limpieza de las columnas LAT y LNG ----------------------------

        for col in ["lat", "lng"]:
            obras[col] = obras[col].astype(str).str.strip()
            obras[col] = obras[col].replace(["", " "], pd.NA)
            obras[col] = obras[col].str.replace(",", ".", regex=False)
            obras[col] = pd.to_numeric(obras[col], errors='coerce')


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
            ])

            db.close()

        except Exception as e:
            print('[ERROR] - mapear_orm -', e)
        
    # @classmethod
    # def cargar_dato(cls):

    #     datos_limpios = cls.limpiar_datos()
    #     for index, row in datos_limpios.iterrows():
    #         entorno = Entorno.get_or_create(nombre=row['entorno'])
    #         etapa = Etapa.get_or_create(nombre=row['etapa'])
    #         tipo = TipoObra.get_or_create(nombre=row['tipo'])
    #         contratacion_tipo = ContratacionTipo.get_or_create(nombre=row['contratacion_tipo'])
    #         area_responsable = AreaResponsable.get_or_create(nombre=row['area_responsable'])
    #         # comuna = Comuna.get_or_create(nombre=row['comuna'])
    #         comuna_name = row['comuna'] # Store the name for debugging
    #         comuna, created_comuna = Comuna.get_or_create(nombre=comuna_name)

    #         # --- ADD THESE DEBUG PRINTS ---
    #         print(f"DEBUG: Processing Comuna: '{comuna_name}'. Object: {comuna} (ID: {comuna.id}), Created: {created_comuna}")
    #         if comuna is None or not hasattr(comuna, 'id') or comuna.id is None:
    #             raise ValueError(f"Comuna object is invalid before creating Barrio: {comuna_name}")
    #         # --- END DEBUG PRINTS ---

    #         barrio = Barrio.get_or_create(nombre=row['barrio'], comuna=comuna)
    #         contratista = Contratista.get_or_create(
    #                 nombre_empresa=row['licitacion_oferta_empresa'],
    #                 cuit_contratista=row['cuit_contratista'],
    #                 nro_contratacion=row['nro_contratacion'],
    #                 expediente_numero=row['expediente-numero'])
    #         
    #         # --- MODIFIED DIRECCION HANDLING ---
    #         lat_val = row['lat']
    #         lng_val = row['lng']

    #         # Convert pandas NaN to None, or handle other non-numeric strings
    #         if pd.isna(lat_val): # Check for pandas NaN
    #             lat_val = None
    #         elif not isinstance(lat_val, (int, float)): # If it's not a number, try converting
    #             try:
    #                 lat_val = float(lat_val)
    #             except (ValueError, TypeError):
    #                 lat_val = None # Set to None if conversion fails

    #         if pd.isna(lng_val): # Check for pandas NaN
    #             lng_val = None
    #         elif not isinstance(lng_val, (int, float)):
    #             try:
    #                 lng_val = float(lng_val)
    #             except (ValueError, TypeError):
    #                 lng_val = None # Set to None if conversion fails

    #         direccion = Direccion.get_or_create(ubicacion=row['direccion'],
    #                               barrio=barrio,
    #                               lat=lat_val,
    #                               lng=lng_val)
    #         obra = Obra(
    #                 entorno=entorno,
    #                 etapa=etapa,
    #                 tipo=tipo,
    #                 contratacion_tipo=contratacion_tipo, 
    #                 area_responsable=area_responsable,
    #                 direccion=direccion, 
    #                 licitacion_oferta_empresa=contratista, 
    #                 nombre=row['nombre'],
    #                 descripcion=row['descripcion'],
    #                 monto_contrato=row['monto_contrato'],
    #                 fecha_inicio=row['fecha_inicio'],
    #                 fecha_fin_inicial=row['fecha_fin_inicial'],
    #                 plazo_meses=row['plazo_meses'],
    #                 porcentaje_avance=row['porcentaje_avance'],
    #                 licitacion_anio=row['licitacion_anio'],
    #                 imagen_1=row['imagen_1'],
    #                 mano_obra=row['mano_obra'],
    #                 destacada=row['destacada'],
    #                 financiamiento=row['financiamiento'])

    #         try:
    #             obra.save()

    #         except Exception as e:
    #             print(f'[ERROR] - Error al grabar en db - {e}')

    #         break

    @classmethod
    def cargar_datos(cls):
        datos_limpios = cls.limpiar_datos() # This should return a pandas DataFrame

        db.connect()
        # Create tables only if they don't exist. Order matters for foreign keys.
        db.create_tables([
            Entorno, Etapa, TipoObra, ContratacionTipo, AreaResponsable,
            Comuna, Barrio, Contratista, Direccion, Obra
        ], safe=True)

        # Helper function for robust float conversion
        def to_float_or_none(value):
            if pd.isna(value):
                return None
            try:
                # Replace comma with dot for decimal if necessary
                if isinstance(value, str):
                    value = value.replace(',', '.')
                return float(value)
            except (ValueError, TypeError):
                return None

        # Helper function for robust int conversion
        def to_int_or_none(value):
            if pd.isna(value):
                return None
            try:
                # Convert to float first to handle decimals before int conversion, then to int
                # E.g., '123.0' -> 123
                if isinstance(value, str):
                    value = value.replace(',', '.')
                return int(float(value))
            except (ValueError, TypeError):
                return None
        
        # Helper function for robust boolean conversion
        def to_bool_or_false(value):
            if pd.isna(value):
                return False # Default to False if NaN, as per model default
            if isinstance(value, str):
                return value.lower() in ['true', '1', 't', 'y', 'yes']
            return bool(value)

        # Helper function for robust date conversion
        def to_date_or_none(value):
            if pd.isna(value): # Handles NaT from pandas
                return None
            
            # If it's already a datetime.date object (e.g., from direct creation or earlier cleaning)
            if isinstance(value, date):
                return value
            
            # If it's a pandas Timestamp object
            if isinstance(value, pd.Timestamp):
                return value.date() # Directly get the date part
            
            # If it's a string, try parsing
            if isinstance(value, str):
                try:
                    return datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    try: # Try another common format
                        return datetime.strptime(value, '%Y/%m/%d').date()
                    except ValueError:
                        pass # Fall through to return None
            
            return None # Return None if none of the above conversions work
        with db.atomic(): # Use a transaction for better performance and atomicity
            for index, row in datos_limpios.iterrows():
                try:
                    # --- 1. Clean and Prepare Data from row ---
                    
                    # Handle potentially missing/NaN categorical fields
                    entorno_name = str(row['entorno']) if pd.notna(row['entorno']) else None
                    etapa_name = str(row['etapa']) if pd.notna(row['etapa']) else None
                    tipo_name = str(row['tipo']) if pd.notna(row['tipo']) else None
                    contratacion_tipo_name = str(row['contratacion_tipo']) if pd.notna(row['contratacion_tipo']) else None
                    area_responsable_name = str(row['area_responsable']) if pd.notna(row['area_responsable']) else None
                    comuna_name = str(row['comuna']) if pd.notna(row['comuna']) else None
                    barrio_name = str(row['barrio']) if pd.notna(row['barrio']) else None
                    
                    # Prepare other fields with robust cleaning
                    lat_val = to_float_or_none(row['lat'])
                    lng_val = to_float_or_none(row['lng'])
                    monto_contrato_val = to_float_or_none(row['monto_contrato'])
                    licitacion_anio_val = to_int_or_none(row['licitacion_anio'])
#                     nro_contratacion_val = to_int_or_none(row['nro_contratacion'])
                    nro_contratacion_val = str(row['nro_contratacion']) if pd.notna(row['nro_contratacion']) else None

                    fecha_inicio_val = to_date_or_none(row['fecha_inicio'])
                    fecha_fin_inicial_val = to_date_or_none(row['fecha_fin_inicial'])
                    destacada_val = to_bool_or_false(row['destacada']) # Assuming 'destacada' is in your cleaned data, even if it's not in the head.
                    
                    # Handle fields that might be missing in some rows but are CharFields
                    descripcion_val = str(row['descripcion']) if pd.notna(row['descripcion']) else None
                    direccion_ubicacion_val = str(row['direccion']) if pd.notna(row['direccion']) else None
                    licitacion_oferta_empresa_name = str(row['licitacion_oferta_empresa']) if pd.notna(row['licitacion_oferta_empresa']) else None
                    cuit_contratista_val = str(row['cuit_contratista']) if pd.notna(row['cuit_contratista']) else None
                    expediente_numero_val = str(row['expediente-numero']) if pd.notna(row['expediente-numero']) else None
                    imagen_1_val = str(row['imagen_1']) if pd.notna(row['imagen_1']) else None
                    financiamiento_val = str(row['financiamiento']) if pd.notna(row['financiamiento']) else None


                    # --- 2. Get or Create Related Entities ---
                    
                    # Only attempt to get/create if the name is not None, otherwise it will cause an error
                    # if the model field itself is NOT NULL.
                    # If these models' 'nombre' field is defined with unique=True AND NOT NULL,
                    # passing None here will cause an error on get_or_create.
                    # If your models allow null for 'nombre' (e.g. Entorno.nombre=CharField(null=True)), then None is fine.
                    entorno = Entorno.get_or_create(nombre=entorno_name)[0] if entorno_name else None
                    etapa = Etapa.get_or_create(nombre=etapa_name)[0] if etapa_name else None
                    tipo = TipoObra.get_or_create(nombre=tipo_name)[0] if tipo_name else None
                    contratacion_tipo = ContratacionTipo.get_or_create(nombre=contratacion_tipo_name)[0] if contratacion_tipo_name else None
                    area_responsable = AreaResponsable.get_or_create(nombre=area_responsable_name)[0] if area_responsable_name else None
                    
                    comuna = Comuna.get_or_create(nombre=comuna_name)[0] if comuna_name else None
                    
                    # Barrio needs a valid Comuna object. If comuna is None, barrio cannot be created.
                    barrio = None
                    if barrio_name and comuna: # Both name and parent object must exist
                        barrio = Barrio.get_or_create(nombre=barrio_name, comuna=comuna)[0]
                    
                    # Contratista: assuming unique by nombre_empresa and cuit_contratista,
                    # but only if nombre_empresa is not None
                    contratista = None
                    if licitacion_oferta_empresa_name: # Must have a name to create/find
                        contratista, _ = Contratista.get_or_create(
                            nombre_empresa=licitacion_oferta_empresa_name,
                            cuit_contratista=cuit_contratista_val,
                            defaults={
                                'nro_contratacion': nro_contratacion_val,
                                'expediente_numero': expediente_numero_val
                            }
                        )

                    # Direccion: Needs a valid Barrio object and ubicacion name
                    direccion = None
                    if direccion_ubicacion_val and barrio: # Both ubicacion and parent object must exist
                        direccion, _ = Direccion.get_or_create(
                            ubicacion=direccion_ubicacion_val,
                            barrio=barrio,
                            defaults={
                                'lat': lat_val,
                                'lng': lng_val
                            }
                        )
                        # Update lat/lng if the existing Direccion was found but had different coordinates
                        # This part is optional based on your exact business logic
                        # if not _ and (direccion.lat != lat_val or direccion.lng != lng_val):
                        #     direccion.lat = lat_val
                        #     direccion.lng = lng_val
                        #     direccion.save()


                    # --- 3. Create and Save Obra Instance ---
                    obra = Obra(
                        entorno=entorno,
                        etapa=etapa,
                        tipo=tipo,
                        contratacion_tipo=contratacion_tipo,
                        area_responsable=area_responsable,
                        direccion=direccion,
                        licitacion_oferta_empresa=contratista,
                        nombre=str(row['nombre']), # Ensure 'nombre' is always a string
                        descripcion=descripcion_val,
                        monto_contrato=monto_contrato_val,
                        fecha_inicio=fecha_inicio_val,
                        fecha_fin_inicial=fecha_fin_inicial_val,
                        plazo_meses=int(row['plazo_meses']), # Already int64, assume always present
                        porcentaje_avance=to_float_or_none(row['porcentaje_avance']), # Assuming it can be float for 100%
                        licitacion_anio=licitacion_anio_val,
                        imagen_1=imagen_1_val,
                        mano_obra=to_int_or_none(row['mano_obra']), # Assuming mano_obra can be empty
                        destacada=destacada_val,
                        financiamiento=financiamiento_val
                    )

                    obra.save()

                except Exception as e:
                    print(f'[ERROR] - Error al grabar en db la fila (Index: {index}): {row.to_dict()} - {e}')
                    # If you want to stop on the first error to debug, uncomment:
                    # raise

        db.close()
    @classmethod
    def nueva_obra(cls):
        pass


    @classmethod
    def obtener_indicadores(cls):
        pass

    @classmethod                                #Agrego un método para desconectar la base de datos
    def desconectar_db(cls):
        try:
            db.close()
        except Exception as e:
            print('\t[ERROR] - desconectando DB\n', e)


if __name__ == '__main__':
    print('\t[DEBUG] - conectando DB')
    GestionarObra.connect_db()
    print('\t[DEBUG] - extrayendo datos (main)')
    GestionarObra.extraer_datos()
    print('\t[DEBUG] - cargando datos')
    GestionarObra.cargar_datos()
    print('\t[DEBUG] - mapeando a la DB')
    GestionarObra.mapear_orm()

