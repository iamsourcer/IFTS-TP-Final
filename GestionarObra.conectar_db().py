from modelo_orm2 import obra, Etapa
from peewee import SqliteDatabase
from datetime import date
from gestionar_obras import GestionarObra

obra = Obra.get_by_id(1)

if __name__ == "__main__":
    # Inicialización y mapeo
    GestionarObra.conectar_db()
    GestionarObra.mapear_orm()

    # Crear al menos dos obras nuevas usando el método de clase
    print("\nCarga de primera obra:")
    obra1 = GestionarObra.nueva_obra()
    print("\nCarga de segunda obra:")
    obra2 = GestionarObra.nueva_obra()

    # Opcional: mostrar las obras creadas
    print("\nObras creadas:")
    for obra in [obra1, obra2]:
        if obra:
            print(f"- {obra.nombre}: {obra.descripcion}")

    # Si tu TP lo pide, puedes avanzar por etapas cada obra aquí...

    # Mostrar indicadores
    GestionarObra.obtener_indicadores()