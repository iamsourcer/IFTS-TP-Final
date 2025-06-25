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
    @abstractmethod
    def extraer_datos(cls):
        pass

    @classmethod
    @abstractmethod
    def conectar_db(cls):
        pass

    @classmethod
    @abstractmethod
    def mapear_orm(cls):
        pass

    @classmethod
    @abstractmethod
    def limpiar_datos(cls):
        pass

    @classmethod
    @abstractmethod
    def cargar_datos(cls):
        pass

    @classmethod
    @abstractmethod
    def nueva_obra(cls):
        pass

    @classmethod
    @abstractmethod
    def obtener_indicadores(cls):
        pass

class GestionarObraConcreta(GestionarObra):
    @classmethod
    def extraer_datos(cls):
        try:
            cls.dataframe = pd.read_csv("obras.csv")
            print("Datos extraídos correctamente del CSV.")
        except Exception as e:
            print(f"Error al extraer datos: {e}")

    @classmethod
    def conectar_db(cls):
        try:
            db.connect()
            print("Conexión a la base de datos realizada.")
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")

    @classmethod
    def mapear_orm(cls):
        try:
            db.create_tables([
                Entorno, Etapa, TipoObra, ContratacionTipo, AreaResponsable,
                Comuna, Barrio, Empresa, FuenteFinanciamiento, Obra
            ])
            print("Tablas creadas/mapeadas correctamente.")
        except Exception as e:
            print(f"Error al mapear las tablas: {e}")

    @classmethod
    def limpiar_datos(cls):
        if cls.dataframe is not None:
            cls.dataframe = cls.dataframe.dropna()
            print("Datos limpiados (nulos eliminados).")
        else:
            print("No hay DataFrame cargado para limpiar.")

    @classmethod
    def cargar_datos(cls):
        if cls.dataframe is None:
            print("No hay datos para cargar.")
            return
        for _, row in cls.dataframe.iterrows():
            try:
                entorno, _ = Entorno.get_or_create(nombre=row['entorno'])
                etapa, _ = Etapa.get_or_create(nombre=row['etapa'])
                tipo_obra, _ = TipoObra.get_or_create(nombre=row['tipo_obra'])
                tipo_contratacion, _ = ContratacionTipo.get_or_create(nombre=row['tipo_contratacion'])
                area, _ = AreaResponsable.get_or_create(nombre=row['area_responsable'])
                comuna, _ = Comuna.get_or_create(nombre=row['comuna'])
                barrio, _ = Barrio.get_or_create(nombre=row['barrio'], comuna=comuna)
                empresa, _ = Empresa.get_or_create(nombre=row['empresa'])
                fuente, _ = FuenteFinanciamiento.get_or_create(nombre=row['fuente_financiamiento'])

                Obra.create(
                    entorno=entorno,
                    etapa=etapa,
                    tipo=tipo_obra,
                    tipo_contratacion=tipo_contratacion,
                    empresa=empresa,
                    area_responsable=area,
                    barrio=barrio,
                    nombre=row['nombre'],
                    descripcion=row['descripcion'],
                    monto_contrato=row['monto_contrato'],
                    licitacion_anio=row['licitacion_anio'],
                    fecha_inicio=row['fecha_inicio'],
                    porcentaje_avance=row['porcentaje_avance'],
                    fecha_fin_inicial=row['fecha_fin_inicial'],
                    plazo_meses=row['plazo_meses'],
                    imagen_1=row.get('imagen_1'),
                    mano_obra=row['mano_obra'],
                    destacada=row['destacada'],
                    fuente_financiamiento=fuente
                )
            except IntegrityError as e:
                print(f"Error de integridad al cargar obra: {e}")
            except Exception as e:
                print(f"Error al cargar obra: {e}")
        print("Datos cargados correctamente.")

    @classmethod
    def nueva_obra(cls):
        print("=== Carga nueva obra ===")
        def pedir_fk(modelo, nombre_campo):
            while True:
                valor = input(f"Ingrese {nombre_campo}: ").strip()
                instancia = modelo.select().where(modelo.nombre == valor).first()
                if instancia:
                    return instancia
                else:
                    print(f"{nombre_campo} no encontrado. Intente de nuevo.")

        entorno = pedir_fk(Entorno, "entorno")
        etapa = Etapa.get_or_create(nombre="Proyecto")[0]
        tipo = pedir_fk(TipoObra, "tipo de obra")
        tipo_contratacion = pedir_fk(ContratacionTipo, "tipo de contratación")
        area = pedir_fk(AreaResponsable, "área responsable")
        comuna = pedir_fk(Comuna, "comuna")
        barrio = pedir_fk(Barrio, "barrio")
        empresa = pedir_fk(Empresa, "empresa")
        fuente = pedir_fk(FuenteFinanciamiento, "fuente de financiamiento")

        nombre = input("Nombre: ")
        descripcion = input("Descripción: ")
        monto_contrato = float(input("Monto del contrato: "))
        licitacion_anio = int(input("Año de licitación: "))
        fecha_inicio = input("Fecha de inicio (YYYY-MM-DD): ")
        fecha_fin_inicial = input("Fecha fin inicial (YYYY-MM-DD): ")
        plazo_meses = int(input("Plazo en meses: "))
        porcentaje_avance = float(input("Porcentaje de avance: "))
        imagen_1 = input("Imagen (opcional): ").strip() or None
        mano_obra = int(input("Mano de obra: "))
        destacada = input("¿Destacada? (s/n): ").strip().lower() == "s"

        obra = Obra(
            entorno=entorno,
            etapa=etapa,
            tipo=tipo,
            tipo_contratacion=tipo_contratacion,
            empresa=empresa,
            area_responsable=area,
            barrio=barrio,
            nombre=nombre,
            descripcion=descripcion,
            monto_contrato=monto_contrato,
            licitacion_anio=licitacion_anio,
            fecha_inicio=fecha_inicio,
            porcentaje_avance=porcentaje_avance,
            fecha_fin_inicial=fecha_fin_inicial,
            plazo_meses=plazo_meses,
            imagen_1=imagen_1,
            mano_obra=mano_obra,
            destacada=destacada,
            fuente_financiamiento=fuente
        )
        try:
            obra.save()
            print("Obra creada con éxito.")
            return obra
        except Exception as e:
            print(f"Error al crear obra: {e}")
            return None

    @classmethod
    def obtener_indicadores(cls):
        print("\n==== Indicadores ====")
        print("Áreas responsables:")
        for a in AreaResponsable.select():
            print("-", a.nombre)
        print("\nTipos de obra:")
        for t in TipoObra.select():
            print("-", t.nombre)
        print("\nCantidad de obras por etapa:")
        for e in Etapa.select():
            cant = Obra.select().where(Obra.etapa == e).count()
            print(f"{e.nombre}: {cant}")
        print("\nCantidad y monto total por tipo de obra:")
        for t in TipoObra.select():
            obras = Obra.select().where(Obra.tipo == t)
            cant = obras.count()
            total = sum([o.monto_contrato for o in obras])
            print(f"{t.nombre}: {cant} obras, ${total}")
        print("\nBarrios de comunas 1, 2 y 3:")
        for cnum in ["1", "2", "3"]:
            comuna = Comuna.select().where(Comuna.nombre == cnum).first()
            if comuna:
                for b in comuna.barrios:
                    print(f"Comuna {cnum}: {b.nombre}")
        print("\nObras finalizadas en <= 24 meses:")
        cant = Obra.select().where((Obra.finalizada == True) & (Obra.plazo_meses <= 24)).count()
        print(f"{cant} obras")
        print("\nMonto total de inversión:")
        total = sum([o.monto_contrato for o in Obra.select()])
        print(f"${total}")


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