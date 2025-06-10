from peewee import SqliteDatabase, AutoField, CharField, DateField, ForeignKeyField, Model, IntegerField, TextField, BooleanField, FloatField

db = SqliteDatabase('observatorio-obras-urbanas.db')

class BaseModel(Model):
    class Meta:
        database = db

class Etapa(BaseModel):
    nombre = CharField(unique=True)

class TipoObra(BaseModel):
    nombre = CharField(unique=True)

class TipoContratacion(BaseModel):
    nombre = CharField()

class Empresa(BaseModel):
    nombre = CharField(unique=True)

class AreaResponsable(BaseModel):
    nombre = CharField()

class Barrio(BaseModel):
    nombre = CharField()


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


    def nuevo_proyect(self):
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




