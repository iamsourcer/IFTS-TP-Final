    GestionarObra.conectar_db()
    GestionarObra.mapear_orm()

    print("\nCarga de primera obra:")
    obra1 = GestionarObra.nueva_obra()
    print("\nCarga de segunda obra:")
    obra2 = GestionarObra.nueva_obra()
    print("\nObras creadas:")
    for obra in [obra1, obra2]:
        if obra:
            print(f"- {obra.nombre}: {obra.descripcion}")

    GestionarObra.obtener_indicadores()