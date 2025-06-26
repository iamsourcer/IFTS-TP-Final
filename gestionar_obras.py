import pandas as pd
from abc import ABC, abstractmethod
from modelos import (
    db, Obra, Entorno, Etapa, TipoObra, ContratacionTipo, AreaResponsable,
    Comuna, Barrio, Empresa, FuenteFinanciamiento
)
from peewee import IntegrityError

class GestionarObra(ABC):
    dataframe = None

   @classmethod    
    def connect_db(cls):
        # Intenta conectar a la base de datos usando Peewee ORM
        # Maneja posibles errores de conexión
        try:
            db.connect()
        except Exception as e:
            print('\t[ERROR] - conectando DB\n', e)
    
    @classmethod
    def extraer_datos(cls):
        # Lee un archivo CSV (observatorio-de-obras-urbanas.csv) usando pandas
        # Maneja errores en la lectura del archivo
        # Retorna un DataFrame con los datos crudos
        try:
            dataframe_crudo = pd.read_csv('observatorio-de-obras-urbanas.csv', sep=';', encoding='latin1')
        except Exception as e:
            print('\t[ERROR] - extraer_datos fallo')
        return dataframe_crudo 

    @classmethod
    def limpiar_datos(cls):
        # Realiza una limpieza exhaustiva de los datos:
        # Elimina acentos de columnas de texto usando unidecode
        # Elimina columnas innecesarias (Unnamed, imágenes, etc.)
        # Elimina duplicados
        # Formatea montos (elimina $, reemplaza comas por puntos)
        # Limpia fechas (convierte a formato datetime)
        # Normaliza valores en columnas como:
            # plazo_meses (reemplaza valores inválidos por 0)
            # porcentaje_avance (elimina % y convierte a número)
            # licitacion_anio, mano_obra, destacada, etc.
        # Normaliza comunas y barrios (unifica nombres y formatos)
        # Limpia coordenadas (latitud y longitud)
        # Maneja valores nulos en campos obligatorios
        obras = cls.extraer_datos()
        
        #----------------------------------------- eliminación de acentos en las columnas de texto -----------------------------------------
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


        # Para comuna y barrio, si hay nan o 0, poner valor por defecto
        obras['comuna'] = obras['comuna'].apply(lambda x: int(x) if pd.notna(x) and str(x).lower() != 'nan' else 0)
        obras['barrio'] = obras['barrio'].apply(lambda x: x if pd.notna(x) and str(x).strip().lower() != 'nan' and x.strip() != '' else 'sin barrio')
        obras['nombre'] = obras['nombre'].apply(lambda x: x if pd.notna(x) and str(x).strip().lower() != 'nan' and x.strip() != '' else 'SIN NOMBRE')
        obras['descripcion'] = obras['descripcion'].apply(lambda x: x if pd.notna(x) and str(x).strip().lower() != 'nan' else ' ')
        obras['direccion'] = obras['direccion'].apply(lambda x: x if pd.notna(x) and str(x).strip().lower() != 'nan' else ' ')

        return obras

    @classmethod    
    def mapear_orm(cls):       
        # Crea las tablas en la base de datos según los modelos ORM definidos
        # Incluye tablas para: Entorno, Etapa, TipoObra, ContratacionTipo, AreaResponsable, Comuna, Barrio, Contratista, Direccion, Obra
        try:
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

        except Exception as e:
            print('[ERROR] - mapear_orm -', e)

    @classmethod
    def cargar_datos(cls):
        # Toma los datos limpios y los carga en la base de datos
        # Para cada fila del DataFrame:
            # Crea o obtiene registros en tablas relacionadas (Entorno, Etapa, etc.)
            # Maneja valores nulos o inválidos
            # Crea la obra principal con todas sus relaciones
        # Incluye manejo especial para coordenadas (lat/lng) y otros campos numéricos
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
                # Este bloque de código es una sección de depuración (debug) que verifica la validez de un objeto comuna antes de usarlo para crear un Barrio.
            #print(f"DEBUG: Processing Comuna: '{comuna_name}'. Object: {comuna} (ID: {getattr(comuna, 'id', None)})")
            #if comuna is None or not hasattr(comuna, 'id') or comuna.id is None:
            #    raise ValueError(f"Comuna object is invalid before creating Barrio: {comuna_name}")
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
        """Crea una nueva obra a partir de datos ingresados por teclado"""
        print("\n--- CREACIÓN DE NUEVA OBRA ---")
        try:
            # Entorno
            while True:
                print("\nEntornos disponibles:")
                for entorno in Entorno.select():
                    print(f"- {entorno.nombre}")
                entorno_nombre = input("Ingrese el entorno de la obra: ").strip()
                entorno = Entorno.get_or_none(Entorno.nombre == entorno_nombre)
                if entorno:
                    break
                print(f"Error: El entorno '{entorno_nombre}' no existe. Intente nuevamente.")
            
            # Etapa
            while True:
                print("\nEtapas disponibles:")
                for etapa in Etapa.select():
                    print(f"- {etapa.nombre}")
                etapa_nombre = input("Ingrese la etapa de la obra: ").strip()
                etapa = Etapa.get_or_none(Etapa.nombre == etapa_nombre)
                if etapa:
                    break
                print(f"Error: La etapa '{etapa_nombre}' no existe. Intente nuevamente.")
            
            # Tipo de obra
            while True:
                print("\nTipos de obra disponibles:")
                for tipo in TipoObra.select():
                    print(f"- {tipo.nombre}")
                tipo_nombre = input("Ingrese el tipo de obra: ").strip()
                tipo = TipoObra.get_or_none(TipoObra.nombre == tipo_nombre)
                if tipo:
                    break
                print(f"Error: El tipo de obra '{tipo_nombre}' no existe. Intente nuevamente.")
            
            # Área responsable
            while True:
                print("\nÁreas responsables disponibles:")
                for area in AreaResponsable.select():
                    print(f"- {area.nombre}")
                area_nombre = input("Ingrese el área responsable: ").strip()
                area = AreaResponsable.get_or_none(AreaResponsable.nombre == area_nombre)
                if area:
                    break
                print(f"Error: El área responsable '{area_nombre}' no existe. Intente nuevamente.")
                
            # Tipo de contratación 
            while True:
                print("\nTipos de contratación disponibles:")
                for contratacion in ContratacionTipo.select():
                    print(f"- {contratacion.nombre}")
                contratacion_nombre = input("Ingrese el tipo de contratación: ").strip()
                contratacion_tipo = ContratacionTipo.get_or_none(ContratacionTipo.nombre == contratacion_nombre)
                if contratacion_tipo:
                    break
                print(f"Error: El tipo de contratación '{contratacion_nombre}' no existe. Intente nuevamente.")
            
            # Comuna y Barrio
            while True:
                print("\nComunas disponibles:")
                for comuna in Comuna.select():
                    print(f"- {comuna.nombre}")
                comuna_nombre = input("Ingrese la comuna: ").strip()
                comuna = Comuna.get_or_none(Comuna.nombre == comuna_nombre)
                if comuna:
                    break
                print(f"Error: La comuna '{comuna_nombre}' no existe. Intente nuevamente.")
            
            barrio_nombre = input("Ingrese el barrio: ").strip()
            barrio, _ = Barrio.get_or_create(nombre=barrio_nombre, comuna=comuna)
            
            # Dirección
            direccion_ubicacion = input("Ingrese la dirección: ").strip()
            lat = input("Ingrese la latitud (opcional, presione Enter para omitir): ").strip()
            lng = input("Ingrese la longitud (opcional, presione Enter para omitir): ").strip()
            
            try:
                lat = float(lat) if lat else None
                lng = float(lng) if lng else None
            except ValueError:
                print("Advertencia: Las coordenadas deben ser números. Se omitirán.")
                lat = lng = None
            
            direccion, _ = Direccion.get_or_create(
                ubicacion=direccion_ubicacion,
                barrio=barrio,
                lat=lat,
                lng=lng
            )
            
            # Contratista
            print("\nDatos del contratista:")
            nombre_empresa = input("Ingrese el nombre de la empresa contratista: ").strip()
            cuit = input("Ingrese el CUIT del contratista: ").strip()
            nro_contratacion = input("Ingrese el número de contratación: ").strip()
            expediente_numero = input("Ingrese el número de expediente: ").strip()
            
            contratista, _ = Contratista.get_or_create(
                nombre_empresa=nombre_empresa,
                cuit_contratista=cuit,
                nro_contratacion=nro_contratacion,
                expediente_numero=expediente_numero
            )
            
            # Datos principales de la obra
            nombre = input("Ingrese el nombre de la obra: ").strip()
            descripcion = input("Ingrese la descripción de la obra: ").strip()
            
            while True:
                try:
                    monto_contrato = float(input("Ingrese el monto del contrato: ").strip())
                    break
                except ValueError:
                    print("Error: El monto debe ser un número. Intente nuevamente.")
            
            fecha_inicio = input("Ingrese la fecha de inicio (YYYY-MM-DD, opcional): ").strip()
            fecha_fin = input("Ingrese la fecha de fin inicial (YYYY-MM-DD, opcional): ").strip()
            
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date() if fecha_inicio else None
                fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date() if fecha_fin else None
            except ValueError:
                print("Advertencia: Formato de fecha incorrecto. Se omitirán las fechas.")
                fecha_inicio = fecha_fin = None
            
            while True:
                try:
                    plazo_meses = int(input("Ingrese el plazo en meses: ").strip())
                    break
                except ValueError:
                    print("Error: El plazo debe ser un número entero. Intente nuevamente.")
            
            while True:
                try:
                    porcentaje_avance = float(input("Ingrese el porcentaje de avance (0-100): ").strip())
                    if 0 <= porcentaje_avance <= 100:
                        break
                    print("Error: El porcentaje debe estar entre 0 y 100.")
                except ValueError:
                    print("Error: El porcentaje debe ser un número. Intente nuevamente.")
            
            while True:
                try:
                    licitacion_anio = int(input("Ingrese el año de licitación: ").strip())
                    break
                except ValueError:
                    print("Error: El año debe ser un número entero. Intente nuevamente.")
            
            mano_obra = input("Ingrese la cantidad de mano de obra (opcional, presione Enter para omitir): ").strip()
            mano_obra = int(mano_obra) if mano_obra else 0
            
            destacada = input("¿Es una obra destacada? (s/n): ").strip().lower()
            destacada = True if destacada == 's' else False
            
            financiamiento = input("Ingrese el tipo de financiamiento (opcional): ").strip()
            
            # Crear la nueva obra
            nueva_obra = Obra(
                entorno=entorno,
                etapa=etapa,
                tipo=tipo,
                contratacion_tipo=contratacion_tipo,
                area_responsable=area,
                direccion=direccion,
                licitacion_oferta_empresa=contratista,
                nombre=nombre,
                descripcion=descripcion,
                monto_contrato=monto_contrato,
                fecha_inicio=fecha_inicio,
                fecha_fin_inicial=fecha_fin,
                plazo_meses=plazo_meses,
                porcentaje_avance=porcentaje_avance,
                licitacion_anio=licitacion_anio,
                mano_obra=mano_obra,
                destacada=destacada,
                financiamiento=financiamiento,
                imagen_1=None  # Puedes agregar lógica para manejar imágenes si es necesario
            )
            
            # Persistir en la base de datos
            nueva_obra.save()
            
            print("\n¡Nueva obra creada exitosamente!")
            print(f"ID de la nueva obra: {nueva_obra.id}")
            
            return nueva_obra
            
        except Exception as e:
            print(f"\n[ERROR] - No se pudo crear la nueva obra: {e}")
            return None
        finally:            
            """Crea una nueva obra a partir de datos ingresados por teclado"""
            print("\n--- CREACIÓN DE NUEVA OBRA ---")       
            
    @classmethod
    def obtener_indicadores(cls):
                    print("\n--- INFORMACION DE LAS OBRAS ---\n")

                    try:
                        print("== Listado de todas las áreas responsables ==")
                        for area in AreaResponsable.select():
                            print(f"  -{area.nombre}")
                        
                        print("\n== Listado de todos los tipos de obra ==")
                        for tip in TipoObra.select():
                            print(f"  -{tip.nombre}")

                        print("\n== Listado de todos los tipos de obras ==")
                        etapas = (Obra.select(Etapa.nombre, fn.COUNT(Obra.id).alias("cantidad"))
                                .join(Etapa)
                                .group_by(Etapa)
                        )
                        for eta in etapas:
                            print(f"  -{eta.etapa.nombre}: {eta.cantidad} obras")
                        
                        print("\n== Obras y monto total por tipo de obra ==")
                        tipos =(Obra.select(TipoObra.nombre, fn.COUNT(Obra.id).alias("cantidad"), fn.SUM(Obra.monto_contrato).alias("monto_total"))
                                .join(TipoObra)
                                .group_by(TipoObra)
                        )
                        for t in tipos:
                            print(f"  - {t.tipo.nombre}: {t.cantidad} obras - Monto total: ${t.monto_total:,.2f}")
                        
                        print("\n== Barrios de comunas ==")
                        barrios = (Barrio.select()
                                .join(Comuna)
                                .where(Comuna.nombre.in_(["1","2","3"]))
                                .order_by(Barrio.nombre)
                                )
                        for b in barrios:
                            print(f"  - {b.nombre} (Comuna {b.comuna.nombre})")

                        print("\n== Obras finalizadas en plazo ≤ 24 meses ==")
                        finalizadas = Obra.select().where(
                        (Obra.etapa == Etapa.get(Etapa.nombre == "Finalizada")) &
                        (Obra.plazo_meses <= 24)
                        )
                        print(f"  - Total: {finalizadas.count()} obras")

                        print("\n== Monto total de inversion ==")
                        monto_total = Obra.select(fn.SUM(Obra.monto_contrato)).scalar()
                        print(f"  - ${monto_total:,.2f}")

                    except Exception as e:
                        print(f"[ERROR] - obtener_indicadores: {e}")
                    
                    db.close()
                    pass
                
    @classmethod                                #Agrego un método para desconectar la base de datos
    def desconectar_db(cls):
                    #Cierra la conexión con la base de datos
                    try:
                        db.close()
                    except Exception as e:
                        print('\t[ERROR] - desconectando DB\n', e)


if __name__ == '__main__':
    print('\t[DEBUG] - conectando DB')
    GestionarObra.connect_db()
    print('\t[DEBUG] - extrayendo datos (main)')
    GestionarObra.extraer_datos()
    print('\t[DEBUG] - mapeando a la DB')
    GestionarObra.mapear_orm()
    print('\t[DEBUG] - cargando datos')
    GestionarObra.cargar_datos()
    print('\t[DEBUG] - nueva obra')
    GestionarObra.nueva_obra()
    print('\t[DEBUG] - obtener indicadores')
    GestionarObra.obtener_indicadores()
    
    
    # Obtener datos limpios
    datos_limpios = GestionarObra.limpiar_datos()
    
    # Mostrar las primeras filas
    # print("\nPrimeras 5 filas de datos limpios:")
    # print(datos_limpios.head())
    
    # Mostrar información general del DataFrame
    # print("\nInformación del DataFrame limpio:")
    # print(datos_limpios.info())
    
    
    
    
