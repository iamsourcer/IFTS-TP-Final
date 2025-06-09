from peewee import from peewee import SqliteDatabase, AutoField, CharField, DateField, ForeignKeyField, Model

db = SqliteDatabase('observatorio-obras-urbanas.db')

class Etapa(Model):
    nombre = CharField()

class TipoObra(Model):
    nombre = CharField()

class TipoContratacion(Model):
    nombre = CharField()

class Empresa(Model):
    nombre = CharField()

class AreaResponsable(Model):
    nombre = CharField()

class Barrio(Model):
    nombre = CharField()


class Obra(Model):
    nombre = CharField()
    descripcion = TextField()
    monto_contrato = IntegerField()
    licitacion_anio = DateField()
    fecha_inicio = DateField()
    porcentaje_avance = FloatField()
    lat = FloatField(null=True)
    lng = FloatField(null=True)
    fecha_fin_inicial = 
    plazo_meses = 
    imagen_1 = 
    imagen_2 = 
    imagen_3 = 
    imagen_4 = 
    licitacion_anio = 
    contratacion_tipo = 
    nro_contratacion = 
    cuit_contratista = 
    beneficiarios = 
    mano_obra = 
    compromiso = 
    destacada = 
    ba_elige = 
    link_interno = 
    pliego_descarga = 
    expediente-numero = 
    estudio_ambiental_descarga = 
    financiamiento = 

