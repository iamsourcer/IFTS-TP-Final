from abc import ABC, abstractmethod
from modelo_orm import db

class GestionarObra(ABC):

    @classmethod
    def extraer_datos(cls):
        pass

    @classmethod
    def conectar_db(cls):
        try:
            db.connect()
        except Exception as e:
            print('[CONNECTION ERROR] -', e)

    @classmethod
    def mapear_orm(cls):
        pass

    @classmethod
    def limpiar_datos(cls):
        pass

    @classmethod
    def cargar_datos(cls):
        pass

    @classmethod
    def nueva_obra(cls):
        pass

    @classmethod
    def obtener_indicadores(cls):
        pass

