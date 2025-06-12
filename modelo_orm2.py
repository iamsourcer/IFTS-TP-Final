from peewee import SqliteDatabase, AutoField, CharField, DateField, ForeignKeyField, Model, IntegerField, TextField, BooleanField, FloatField

db = SqliteDatabase('observatorio-obras-urbanas.db')


class BaseModel(Model):
    class Meta:
        database = db

class Entorno(BaseModel):
    nombre = CharField(unique=True)

class Etapa(BaseModel):
    nombre = CharField(unique=True)

class TipoObra(BaseModel):
    nombre = CharField(unique=True)

class ContratacionTipo(BaseModel):
    nombre = CharField()

class AreaResponsable(BaseModel):
    nombre = CharField()

class Barrio(BaseModel):
    nombre = CharField()

class Comuna(BaseModel):
    nombre = CharField()

class Contratista(BaseModel):
    nombre_empresa = CharField()
    cuit_contratista = CharField() 

class Direccion(BaseModel):
    ubicacion = CharField()
    barrio = ForeignKeyField(Barrio, backref='direcciones')  
    comuna = ForeignKeyField(Comuna, backref='direcciones')
    lat = FloatField(null=True)
    lng = FloatField(null=True)

class Obra(BaseModel):
    etapa = ForeignKeyField(Etapa, backref='obras')
    tipo = ForeignKeyField(TipoObra, backref='obras')
    contratacion_tipo = ForeignKeyField(ContratacionTipo, backref='obras')
    area_responsable = ForeignKeyField(AreaResponsable, backref='obras') 
    direccion = ForeignKeyField(Direccion, backref='obras')

    nombre = CharField()
    descripcion = TextField()
    monto_contrato = FloatField()
    fecha_inicio = DateField()
    porcentaje_avance = FloatField()
    fecha_fin_inicial = DateField() 
    plazo_meses = IntegerField() 
    licitacion_oferta_empresa = ForeignKeyField(Contratista, backref='obras')
    licitacion_anio = IntegerField()
    nro_contratacion = IntegerField() 
    expediente_numero = CharField(max_length=512, null=True) 
    imagen_1 = CharField(max_length=512, null=True)



    def nuevo_proyecto(self):
        ...

    def iniciar_contratacion(self):
        ...

    def adjudicar_obra(self):
        ...

    def iniciar_obra(self):
        ...

    def actualizar_porcentaje_avance(self):
        ...

    def incrementar_plazo(self):
        ...

    def incrementar_mano_obra(self):
        ...

    def finalizar_obra(self):
        ...

    def rescindir_obra(self):
        ...





