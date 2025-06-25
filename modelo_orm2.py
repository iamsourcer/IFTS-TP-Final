from peewee import SqliteDatabase, AutoField, CharField, DateField, ForeignKeyField, Model, IntegerField, TextField, BooleanField, FloatField

db = SqliteDatabase('observatorio-obras-urbanas.db')

class BaseModel(Model):
    class Meta:
        database = db

class Entorno(BaseModel):
    nombre = CharField(unique=True)
    class Meta:
        db_table = "entornos"

class Etapa(BaseModel):
    nombre = CharField(unique=True)
    class Meta:
        db_table = "etapas"

class TipoObra(BaseModel):
    nombre = CharField(unique=True)
    class Meta:
        db_table = "tipo_obras"

class ContratacionTipo(BaseModel):
    nombre = CharField()
    class Meta:
        db_table = "contratacion_tipo"

class AreaResponsable(BaseModel):
    nombre = CharField()
    class Meta:
        db_table = "area_responsable"

class Comuna(BaseModel):
    nombre = CharField(unique=True)
    class Meta:
        db_table = "comunas"

class Barrio(BaseModel):
    nombre = CharField(unique=True)
    comuna = ForeignKeyField(Comuna, backref='barrios')
    class Meta:
        db_table = "barrios"

class Contratista(BaseModel):
    nombre_empresa = CharField()
    cuit_contratista = CharField() 
    nro_contratacion = IntegerField() 
    expediente_numero = CharField(max_length=512, null=True)
    class Meta:
        db_table = "contratistas"

class Direccion(BaseModel):
    ubicacion = CharField()
    barrio = ForeignKeyField(Barrio, backref='direcciones')
    lat = FloatField(null=True)
    lng = FloatField(null=True)
    class Meta:
        db_table = "direccion"


class Obra(BaseModel):
    etapa = ForeignKeyField(Etapa, backref='obras')
    tipo = ForeignKeyField(TipoObra, backref='obras')
    tipo_contratacion = ForeignKeyField(TipoContratacion, backref='obras')
    empresa = ForeignKeyField(Empresa, backref='obras')
    area_responsable = ForeignKeyField(AreaResponsable, backref='obras') 
    barrio = ForeignKeyField(Barrio, backref='obras')  
    nombre = CharField()
    descripcion = TextField()
    monto_contrato = FloatField()
    licitacion_anio = IntegerField()
    fecha_inicio = DateField()
    porcentaje_avance = FloatField()
    lat = FloatField(null=True)
    lng = FloatField(null=True)
    fecha_fin_inicial = DateField() 
    plazo_meses = IntegerField() 
    imagen_1 = CharField(max_length=512, null=True)
    imagen_2 = CharField(max_length=512, null=True) 
    imagen_3 = CharField(max_length=512, null=True) 
    imagen_4 = CharField(max_length=512, null=True) 
    nro_contratacion = IntegerField() 
    cuit_contratista = CharField() 
    beneficiarios = CharField() 
    mano_obra = IntegerField() 
    compromiso = BooleanField() 
    destacada =  BooleanField()
    link_interno = CharField(max_length=512, null=True) 
    pliego_descarga = CharField(max_length=512, null=True)
    expediente_numero = CharField(max_length=512, null=True) 
    finalizada = BooleanField(default=False)
    rescindida = BooleanField(default=False)

    class Meta:
        db_table = "obras"

    def nuevo_proyecto(self):
        self.etapa = Etapa.get(Etapa.nombre == "Proyecto")
        self.porcentaje_avance = 0
        self.save()
        
    def iniciar_contratacion(self):
        self.etapa = Etapa.get(Etapa.nombre == "Licitación")
        self.save()

    """ 10. Para adjudicar la obra a una empresa, se debe invocar al método adjudicar_obra() y
asignarle la Empresa (debe ser una empresa existente en la BD) y el nro_expediente."""
  
    def adjudicar_obra(self):
        self.empresa = empresa
        self.expediente_numero = str(nro_expediente)
        self.etapa = Etapa.get(Etapa.nombre == "Adjudicada")
        self.save()

#   Invocar al método adjudicar_obra() de la clase Obra, asignándole una instancia de Empresa: 
#   empresa = Empresa.get(Empresa.nombre == "nombre random.")
#   obra = Obra.get_by_id(1)
#   obra.adjudicar_obra(empresa, "Expediente random")"""
   

    """ 11. Para indicar el inicio de la obra, se debe invocar al método iniciar_obra(), y asignarle valores
        a los siguientes atributos: destacada, fecha_inicio, fecha_fin_inicial, fuente_financiamiento
        (debe ser un valor existente en la BD) y mano_obra."""

    def iniciar_obra(self):
        self.destacada = destacada 
        self.fecha_inicio = fecha_inicio
        self.fecha_fin_inicial = fecha_fin_inicial
        self.mano_obra = mano_obra
        self.etapa = Etapa.get(Etapa.nombre == "En Ejecucion")
        self.save()

# Invocar al método iniciar_obra() de la clase Obra, asignándole los valores correspondientes:
# from datetime import date
# fuente = FuenteFinanciamiento.get(FuenteFinanciamiento.nombre == "Nacional")
# obra = Obra.get_by_id(1)
# obra.iniciar_obra(
#     destacada=True,
#     fecha_inicio=date(2025, 7, 1),
#     fecha_fin_inicial=date(2026, 7, 1),
#     fuente_financiamiento=fuente,
#     mano_obra="Contratada"
# )       

    
    def actualizar_porcentaje_avance(self, valor):
        if 0 <= valor <= 100:
            self.porcentaje_avance = valor
            self.save()
        else:
            raise ValueError("El porcentaje de avance debe estar entre 0 y 100.")

    
    def incrementar_plazo(self, dias):
        self.plazo_dias += dias
        self.save()

    
    def incrementar_mano_obra(self, cantidad):
        self.mano_obra += cantidad
        self.save()

    
    def finalizar_obra(self):
        self.etapa = Etapa.get(Etapa.nombre == "Finalizada")
        self.porcentaje_avance = 100
        self.finalizada = True
        self.save()

    
    def rescindir_obra(self):
        self.rescindida = True
        self.etapa = Etapa.get(Etapa.nombre == "Rescindida")
        self.save()

    from gestionar_obra import GestionarObra
    # Crear al menos dos obras usando el método de clase
    print("Cargar la primera obra:")
    obra1 = GestionarObra.nueva_obra()

    print("\nCargar la segunda obra:")
    obra2 = GestionarObra.nueva_obra()

    print("\nObras creadas:")
    print(obra1)
    print(obra2)



